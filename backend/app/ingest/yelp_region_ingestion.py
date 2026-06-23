"""
Yelp Fusion API ingestion script for Matcha Scout — high-coverage edition.

Supports San Diego and Orange County with:
- Production write guards (--apply --production --confirm-production)
- Multi-term, multi-location sweeps with deduplication
- Hard API call cap (--max-api-calls) to protect the Yelp trial limit
- Pagination up to 50 businesses per call
- No review excerpts by default (--include-reviews must be explicit)
- Detailed summary of calls used, cafes found, and duplicates skipped

Usage — local:
    # Dry-run (no writes, no real Yelp calls needed — actually does call Yelp for the list)
    python -m app.ingest.yelp_region_ingestion \\
        --region san-diego --target-per-region 20 \\
        --no-reviews --dry-run --request-delay 0.6

    # Apply locally
    python -m app.ingest.yelp_region_ingestion \\
        --region orange-county --term-set matcha-discovery \\
        --target-per-region 150 --max-api-calls 500 \\
        --no-reviews --apply --local --request-delay 0.6

Usage — production:
    # Production apply (all three flags required)
    python -m app.ingest.yelp_region_ingestion \\
        --region san-diego --term-set matcha-discovery \\
        --target-per-region 150 --max-api-calls 500 \\
        --no-reviews --apply --production --confirm-production \\
        --request-delay 0.6
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.services import db
from app.services.regions import (
    get_discovery_locations,
    get_term_set,
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

# Yelp Fusion returns max 50 businesses per search call.
YELP_MAX_PER_REQUEST = 50


def _postgres_configured() -> bool:
    value = getattr(settings, "database_url", None)
    return isinstance(value, str) and bool(value)


# ── Call counter ──────────────────────────────────────────────────────────────

@dataclass
class CallCounter:
    max_calls: int
    used: int = 0
    search_calls: int = 0
    review_calls: int = 0

    def can_make_call(self) -> bool:
        return self.used < self.max_calls

    def record_search(self) -> None:
        self.used += 1
        self.search_calls += 1

    def record_review(self) -> None:
        self.used += 1
        self.review_calls += 1

    def remaining(self) -> int:
        return max(0, self.max_calls - self.used)

    def summary(self) -> str:
        return (
            f"API calls used: {self.used}/{self.max_calls} "
            f"(search={self.search_calls}, review={self.review_calls}, "
            f"remaining={self.remaining()})"
        )


# ── Multi-term deduplication sweep ───────────────────────────────────────────

def sweep_businesses(
    terms: list[str],
    locations: list[str],
    target: int,
    counter: CallCounter,
    request_delay: float,
) -> tuple[list[dict], int]:
    """
    Search across all (term, location) combinations, paginating as needed.

    Returns:
        (unique_businesses, duplicates_skipped)

    Stops when:
        - target unique businesses reached
        - max_api_calls reached
        - all combos exhausted
    """
    seen_ids: set[str] = set()
    unique: list[dict] = []
    duplicates_skipped = 0

    for term in terms:
        if len(unique) >= target or not counter.can_make_call():
            break
        for location in locations:
            if len(unique) >= target or not counter.can_make_call():
                break

            offset = 0
            while len(unique) < target and counter.can_make_call():
                per_call = min(YELP_MAX_PER_REQUEST, target - len(unique))

                try:
                    counter.record_search()
                    results = search_businesses(term, location, per_call, offset)
                except YelpApiError as exc:
                    print(f"  Warning [{term!r}/{location!r} offset={offset}]: {exc}", file=sys.stderr)
                    break

                if not results:
                    break  # No more results for this combo

                new_this_page = 0
                for biz in results:
                    if biz["id"] not in seen_ids:
                        seen_ids.add(biz["id"])
                        unique.append(biz)
                        new_this_page += 1
                        if len(unique) >= target:
                            break
                    else:
                        duplicates_skipped += 1

                if len(results) < per_call:
                    break  # Yelp returned fewer than requested — no more pages

                offset += len(results)
                time.sleep(request_delay)

            time.sleep(request_delay)  # Brief pause between location combos

    return unique, duplicates_skipped


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "High-coverage Yelp Fusion API ingestion for Matcha Scout. "
            "Requires explicit --local OR --production --confirm-production to write."
        )
    )
    parser.add_argument(
        "--region", required=True,
        choices=["san-diego", "orange-county"],
        help="Region to ingest.",
    )
    parser.add_argument("--location", default=None,
        help="Override: use a single custom location instead of the region defaults.")
    parser.add_argument("--term", default=None,
        help="Single search term. Overrides --term-set.")
    parser.add_argument("--term-set", default="matcha",
        choices=["matcha", "matcha-discovery"],
        help="Named search term set to use. 'matcha-discovery' uses 6 terms for broader coverage.")
    parser.add_argument("--target-per-region", "--limit", dest="target", type=int, default=20,
        help="Max unique cafes to collect per region (default: 20).")
    parser.add_argument("--max-api-calls", type=int, default=200,
        help="Hard limit on Yelp API calls for this run (default: 200). "
             "Protects against exceeding the 5,000-call monthly trial limit.")
    parser.add_argument("--high-coverage", action="store_true",
        help="Use the extended city list for the region instead of defaults.")
    parser.add_argument("--no-reviews", action="store_true",
        help="Do NOT fetch Yelp review excerpts (recommended for bulk ingestion).")
    parser.add_argument("--include-reviews", action="store_true",
        help="Fetch up to 3 Yelp review excerpts per cafe (uses extra API calls).")
    parser.add_argument("--request-delay", type=float, default=0.6,
        help="Seconds between Yelp API calls (default: 0.6 to respect rate limits).")
    parser.add_argument("--no-overwrite", action="store_true",
        help="Preserve existing user-owned fields when updating existing cafe records.")
    parser.add_argument("--dry-run", action="store_true",
        help="Preview only — no database writes. Default when --apply is not given.")

    # Write mode: mutually exclusive local vs production
    write_group = parser.add_argument_group("Write mode (choose exactly one with --apply)")
    write_group.add_argument("--apply", action="store_true",
        help="Write to the database (requires --local or --production --confirm-production).")
    write_group.add_argument("--local", action="store_true",
        help="Write to the local database (Docker Compose).")
    write_group.add_argument("--production", action="store_true",
        help="Write to the production database. "
             "Requires --confirm-production to prevent accidents.")
    write_group.add_argument("--confirm-production", action="store_true",
        help="Explicit confirmation that you intend to write to production.")

    return parser.parse_args()


def _validate_write_mode(args: argparse.Namespace) -> tuple[bool, str]:
    """
    Validate write flags. Returns (is_production, error_message_or_empty).
    """
    if not args.apply:
        return False, ""

    if args.local and args.production:
        return False, "--local and --production are mutually exclusive."

    if args.local:
        if _postgres_configured() and settings.database_environment != "local":
            return False, (
                "--apply --local requires DATABASE_ENVIRONMENT=local."
            )
        if not _postgres_configured() and not settings.dynamodb_endpoint_url:
            return False, (
                "--apply --local requires DYNAMODB_ENDPOINT_URL to be set. "
                "Is Docker Compose running?"
            )
        return False, ""  # local write, no error

    if args.production:
        if not args.confirm_production:
            return True, (
                "--apply --production requires --confirm-production. "
                "This prevents accidental production writes."
            )
        if _postgres_configured() and settings.database_environment != "production":
            return True, (
                "--apply --production requires DATABASE_ENVIRONMENT=production."
            )
        return True, ""  # production write confirmed, no error

    # --apply without --local or --production
    return False, (
        "--apply requires either --local (Docker Compose) or "
        "--production --confirm-production (production database)."
    )


def run(args: argparse.Namespace) -> int:
    applying = args.apply

    # Validate write mode
    is_production, write_error = _validate_write_mode(args)
    if write_error:
        print(f"ERROR: {write_error}", file=sys.stderr)
        return 2

    # Determine terms
    if args.term:
        terms = [args.term]
    else:
        try:
            terms = get_term_set(args.term_set)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    # Determine locations
    if args.location:
        locations = [args.location]
    else:
        locations = get_discovery_locations(args.region, high_coverage=args.high_coverage)

    # Reviews mode
    fetch_reviews = args.include_reviews and not args.no_reviews

    region_key, region_label = normalize_region(args.region)
    counter = CallCounter(max_calls=args.max_api_calls)
    ingested_at = datetime.now(timezone.utc).isoformat()

    # ── Mode banner ───────────────────────────────────────────────────────────
    mode = "APPLY (PRODUCTION)" if is_production else ("APPLY (LOCAL)" if applying else "DRY RUN")
    print(f"\n{'='*64}")
    print(f"{mode}: {region_label}")
    print(f"{'='*64}")
    print(f"  Terms ({len(terms)}): {terms}")
    print(f"  Locations ({len(locations)}): {locations if len(locations) <= 4 else f'{len(locations)} cities'}")
    print(f"  Target: {args.target} unique cafes")
    print(f"  Max API calls: {args.max_api_calls}")
    print(f"  Fetch reviews: {fetch_reviews}")
    print(f"  Reviews note: Yelp review excerpts are stored separately; they do NOT")
    print(f"                affect Matcha Scout taste-profile confidence scores.")
    print()

    if is_production:
        print("  ⚠️  PRODUCTION WRITE — will write to the configured production database")
        print()

    # ── Sweep ────────────────────────────────────────────────────────────────
    businesses, duplicates_skipped = sweep_businesses(
        terms, locations, args.target, counter, args.request_delay
    )

    if not businesses:
        print("No Yelp businesses found matching search criteria.")
        print(f"  {counter.summary()}")
        return 0

    print(f"  Unique businesses found: {len(businesses)}")
    print(f"  Duplicates skipped across term/location combos: {duplicates_skipped}")
    print()

    # ── Per-business processing ───────────────────────────────────────────────
    created_count = 0
    updated_count = 0
    failed_count = 0

    for business in businesses:
        cafe = normalize_yelp_business(
            business,
            location_label=locations[0] if len(locations) == 1 else region_label,
            ingested_at=ingested_at,
        )
        cafe["region_key"] = region_key
        cafe["region_label"] = region_label

        reviews = []
        if fetch_reviews and counter.can_make_call():
            time.sleep(args.request_delay)
            try:
                counter.record_review()
                reviews = [
                    normalize_yelp_review_excerpt(review, index=i, ingested_at=ingested_at)
                    for i, review in enumerate(get_business_reviews(business["id"]))
                ]
            except YelpApiError as exc:
                print(f"  Warning: could not fetch reviews for {cafe['name']!r}: {exc}", file=sys.stderr)

        # Preview (show top 20 in dry-run, all in apply mode)
        _print_preview(cafe, len(reviews))

        if applying:
            try:
                existing = db.get_item(pk=f"CAFE#{cafe['cafe_id']}", sk="METADATA")
                saved = db.upsert_cafe_from_external_source(cafe, no_overwrite=args.no_overwrite)
                if existing:
                    updated_count += 1
                else:
                    created_count += 1
                for review in reviews:
                    db.put_external_review_excerpt(saved["cafe_id"], review)
            except Exception as exc:
                print(f"  ERROR writing {cafe.get('name')!r}: {exc}", file=sys.stderr)
                failed_count += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(f"── Summary: {region_label} ──")
    print(f"  Unique businesses: {len(businesses)}")
    if applying:
        print(f"  Created: {created_count}")
        print(f"  Updated: {updated_count}")
        print(f"  Failed:  {failed_count}")
    else:
        print(f"  (Dry run — no writes)")
    print(f"  Duplicates skipped: {duplicates_skipped}")
    print(f"  {counter.summary()}")

    if not applying:
        print()
        print("Dry run complete. Re-run with:")
        if is_production or (args.production if hasattr(args, 'production') else False):
            print("  --apply --production --confirm-production")
        else:
            print("  --apply --local")

    return 0 if failed_count == 0 else 1


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


def _print_preview(cafe: dict, review_count: int) -> None:
    cats = cafe.get("categories") or []
    cat_str = ", ".join(cats[:3]) if cats else "n/a"
    print(
        f"  • {cafe['name']} | {cafe.get('location', '?')} | "
        f"★{cafe.get('rating', '?')} ({cafe.get('review_count', '?')} reviews) | "
        f"[{cat_str}]"
    )
    if cafe.get("address"):
        print(f"    {cafe['address']}")


if __name__ == "__main__":
    main()
