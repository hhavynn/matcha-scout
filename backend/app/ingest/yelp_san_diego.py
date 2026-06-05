from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from app.core.config import settings
from app.services import db
from app.services.yelp_client import (
    YelpApiError,
    YelpApiKeyMissingError,
    get_business_reviews,
    normalize_yelp_business,
    normalize_yelp_review_excerpt,
    search_businesses,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or locally ingest San Diego cafe metadata from the official Yelp Fusion API."
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--term", default=settings.yelp_default_term)
    parser.add_argument("--location", default=settings.yelp_default_location)
    parser.add_argument("--include-reviews", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Preview only. This is the default unless --apply is set.")
    parser.add_argument("--apply", action="store_true", help="Write to local DynamoDB. Requires --local.")
    parser.add_argument("--local", action="store_true", help="Confirm this run targets local/admin DynamoDB only.")
    parser.add_argument("--no-overwrite", action="store_true", help="Preserve existing user-owned cafe fields when updating.")
    return parser.parse_args()


def _print_preview(cafe: dict, review_count: int) -> None:
    print(
        f"- {cafe['name']} [{cafe['cafe_id']}] "
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
        print("--apply requires --local. Production ingestion is intentionally unsupported in Phase 11.", file=sys.stderr)
        return 2

    if applying and not settings.dynamodb_endpoint_url:
        print("Refusing to apply without DYNAMODB_ENDPOINT_URL. Phase 11 ingestion is local-only.", file=sys.stderr)
        return 2

    ingested_at = datetime.now(timezone.utc).isoformat()
    businesses = search_businesses(args.term, args.location, args.limit, args.offset)

    mode = "APPLY" if applying else "DRY RUN"
    print(f"{mode}: Yelp business search term={args.term!r} location={args.location!r} limit={args.limit} offset={args.offset}")

    for business in businesses:
        cafe = normalize_yelp_business(business, location_label=args.location, ingested_at=ingested_at)
        reviews = []
        if args.include_reviews:
            reviews = [
                normalize_yelp_review_excerpt(review, index=i, ingested_at=ingested_at)
                for i, review in enumerate(get_business_reviews(business["id"]))
            ]

        _print_preview(cafe, len(reviews))

        if applying:
            saved = db.upsert_cafe_from_external_source(cafe, no_overwrite=args.no_overwrite)
            for review in reviews:
                db.put_external_review_excerpt(saved["cafe_id"], review)

    if not businesses:
        print("No Yelp businesses returned.")

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
