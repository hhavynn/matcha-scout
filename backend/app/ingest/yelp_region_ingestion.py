"""
Generic Yelp Fusion API ingestion script for Matcha Scout.

Supports San Diego and Orange County. For Orange County, automatically
searches across multiple cities and deduplicates by Yelp business ID.

Usage:
    # San Diego dry-run
    python -m app.ingest.yelp_region_ingestion \\
        --region san-diego --limit 20 --include-reviews --dry-run

    # Orange County dry-run (multi-city search)
    python -m app.ingest.yelp_region_ingestion \\
        --region orange-county --limit 20 --include-reviews --dry-run \\
        --request-delay 0.6

    # Apply Orange County locally
    python -m app.ingest.yelp_region_ingestion \\
        --region orange-county --limit 20 --include-reviews \\
        --apply --local --request-delay 0.6

    # Override location (single city)
    python -m app.ingest.yelp_region_ingestion \\
        --region orange-county --location "Irvine, CA" \\
        --limit 10 --include-reviews --dry-run
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.services import db
from app.services.regions import (
    OC_DEFAULT_LOCATIONS,
    SD_DEFAULT_LOCATION,
    normalize_region,
)
from app.services.yelp_client import (
    YelpApiError,
    YelpApiKeyMissingError,
    get_business_reviews,
    normalize_yelp_business,
    normalize_yelp_review_excerpt,
    search_businesses,
)

# Per-city search cap to avoid wasting API quota on a single city.
_PER_CITY_CAP = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest real cafe metadata from the official Yelp Fusion API into local DynamoDB."
    )
    parser.add_argument(
        "--region", required=True,
        choices=["san-diego", "orange-county"],
        help="Region to ingest. Determines default search location(s) and tags cafes.",
    )
    parser.add_argument("--location", default=None,
        help="Override the default search location (single city/area). "
             "For orange-county without this flag, searches multiple OC cities.")
    parser.add_argument("--term", default=settings.yelp_default_term)
    parser.add_argument("--limit", type=int, default=20,
        help="Max unique cafes to return/apply (after deduplication).")
    parser.add_argument("--offset", type=int, default=0,
        help="Offset for single-location searches only.")
    parser.add_argument("--include-reviews", action="store_true",
        help="Fetch up to 3 Yelp review excerpts per cafe.")
    parser.add_argument("--dry-run", action="store_true",
        help="Preview only. Default when --apply is not given.")
    parser.add_argument("--apply", action="store_true",
        help="Write to local DynamoDB. Requires --local.")
    parser.add_argument("--local", action="store_true",
        help="Confirm this run targets local DynamoDB only.")
    parser.add_argument("--no-overwrite", action="store_true",
        help="Preserve existing user-owned fields when refreshing Yelp metadata.")
    parser.add_argument("--request-delay", type=float, default=0.5,
        help="Seconds between Yelp API calls to respect per-second rate limits (default: 0.5).")
    return parser.parse_args()


def _search_locations_for_region(region: str, location_override: Optional[str]) -> list[str]:
    """Return the ordered list of Yelp search locations for a region."""
    if location_override:
        return [location_override]
    if region == "san-diego":
        return [SD_DEFAULT_LOCATION]
    if region == "orange-county":
        return OC_DEFAULT_LOCATIONS
    return [location_override or "San Diego, CA"]


def fetch_unique_businesses(
    term: str,
    locations: list[str],
    limit: int,
    offset: int,
    request_delay: float,
) -> list[dict]:
    """Search across locations, deduplicate by Yelp business id, return up to limit results."""
    seen_ids: set[str] = set()
    unique: list[dict] = []

    # For a single location, use the full limit. For multi-city, cap per city so
    # no one city monopolizes the result set.
    per_city = limit if len(locations) == 1 else max(1, min(_PER_CITY_CAP, limit))

    for location in locations:
        if len(unique) >= limit:
            break
        try:
            results = search_businesses(term, location, per_city, offset if len(locations) == 1 else 0)
        except YelpApiError as exc:
            print(f"  Warning: Yelp API error for {location!r}: {exc}", file=sys.stderr)
            continue

        new_count = 0
        for biz in results:
            if biz["id"] not in seen_ids:
                seen_ids.add(biz["id"])
                unique.append(biz)
                new_count += 1
                if len(unique) >= limit:
                    break

        if len(locations) > 1:
            print(f"  Searched {location!r}: {len(results)} results, {new_count} new unique")
            time.sleep(request_delay)

    return unique[:limit]


def _print_preview(cafe: dict, review_count: int) -> None:
    print(
        f"- {cafe['name']} [{cafe['cafe_id']}] "
        f"region={cafe.get('region_key', 'n/a')} "
        f"rating={cafe.get('rating', 'n/a')} reviews={cafe.get('review_count', 'n/a')} "
        f"external_excerpts={review_count}"
    )
    if cafe.get("address"):
        print(f"  {cafe['address']}")
    if cafe.get("external_url"):
        print(f"  Yelp: {cafe['external_url']}")


def run(args: argparse.Namespace) -> int:
    applying = args.apply
    if applying and not args.local:
        print(
            "ERROR: --apply requires --local. Production ingestion is not supported.",
            file=sys.stderr,
        )
        return 2

    if applying and not settings.dynamodb_endpoint_url:
        print(
            "ERROR: --apply refused — DYNAMODB_ENDPOINT_URL not set. "
            "Run with Docker Compose (local mode only).",
            file=sys.stderr,
        )
        return 2

    region_key, region_label = normalize_region(args.region)
    locations = _search_locations_for_region(args.region, args.location)
    mode = "APPLY" if applying else "DRY RUN"

    print(
        f"{mode}: region={region_key!r} ({region_label}) "
        f"term={args.term!r} limit={args.limit} "
        f"locations={locations if len(locations) <= 3 else f'{len(locations)} cities'}"
    )

    ingested_at = datetime.now(timezone.utc).isoformat()

    if len(locations) > 1:
        print(f"  Multi-city search across {len(locations)} locations:")
    businesses = fetch_unique_businesses(
        args.term, locations, args.limit, args.offset, args.request_delay
    )

    if not businesses:
        print("No Yelp businesses returned.")
        if not applying:
            print("\nDry run only. Re-run with --apply --local to write to local DynamoDB.")
        return 0

    print(f"  Unique businesses found: {len(businesses)}")
    print()

    for business in businesses:
        cafe = normalize_yelp_business(
            business,
            location_label=locations[0] if len(locations) == 1 else region_label,
            ingested_at=ingested_at,
        )
        # Tag with region
        cafe["region_key"] = region_key
        cafe["region_label"] = region_label

        reviews = []
        if args.include_reviews:
            time.sleep(args.request_delay)
            try:
                reviews = [
                    normalize_yelp_review_excerpt(review, index=i, ingested_at=ingested_at)
                    for i, review in enumerate(get_business_reviews(business["id"]))
                ]
            except YelpApiError as exc:
                print(f"  Warning: could not fetch reviews for {cafe['name']!r}: {exc}", file=sys.stderr)

        _print_preview(cafe, len(reviews))

        if applying:
            saved = db.upsert_cafe_from_external_source(cafe, no_overwrite=args.no_overwrite)
            for review in reviews:
                db.put_external_review_excerpt(saved["cafe_id"], review)

    if not applying:
        print("\nDry run only. Re-run with --apply --local to write to local DynamoDB.")
    return 0


def main() -> None:
    args = parse_args()
    try:
        raise SystemExit(run(args))
    except YelpApiKeyMissingError as exc:
        print(f"Yelp config error: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except YelpApiError as exc:
        print(f"Yelp API error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
