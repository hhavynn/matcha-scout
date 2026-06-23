"""
Curation target export for Matcha Scout.

Reads cafe records from the configured local or production database and writes a
gitignored local checklist — either Markdown or JSON — listing cafes
ranked by "curation priority" so you know which to verify first.

Curation priority = how likely a venue actually serves notable matcha.
Scored from keywords in name+categories and weighted by popularity.

This script:
  - NEVER calls the Yelp API
  - NEVER writes to the database
  - NEVER creates or modifies drinks
  - NEVER scrapes any website
  - NEVER commits output files (they are gitignored)

Usage:
    # Local DynamoDB (Docker Compose running)
    python -m app.ingest.export_curation_targets \\
        --region san-diego --source local \\
        --output data/curation/my-san-diego-production-curation.local.md

    # Production DynamoDB
    python -m app.ingest.export_curation_targets \\
        --region orange-county --source production \\
        --output data/curation/my-orange-county-production-curation.local.md

    # JSON output, top 25, min rating 4.0
    python -m app.ingest.export_curation_targets \\
        --region all --source production \\
        --format json --limit 25 --min-rating 4.0 \\
        --output data/curation/my-top-cafes.local.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.services import db


def _postgres_configured() -> bool:
    value = getattr(settings, "database_url", None)
    return isinstance(value, str) and bool(value)


# ── Curation priority scoring ─────────────────────────────────────────────────

# Name/category keyword weights — higher = more likely to serve notable matcha
_NAME_KEYWORDS: dict[str, float] = {
    "matcha": 10.0,
    "tea": 5.0,
    "boba": 4.0,
    "bubble": 4.0,
    "japanese": 3.0,
    "dessert": 2.5,
    "mochi": 3.0,
    "uji": 4.0,
    "ceremonial": 4.0,
    "hojicha": 3.5,
    "sencha": 3.0,
    "cafe": 1.0,
    "coffee": 0.5,
    "bakery": 1.0,
    "patisserie": 1.5,
    "asian": 1.0,
    "korean": 1.0,
    "vietnamese": 0.5,
}

_CATEGORY_KEYWORDS: dict[str, float] = {
    "tea rooms": 8.0,
    "bubble tea": 6.0,
    "coffee & tea": 4.0,
    "japanese": 4.0,
    "desserts": 3.0,
    "ice cream & frozen yogurt": 2.0,
    "bakeries": 1.5,
    "cafes": 1.0,
    "patisserie/cake shop": 2.0,
    "themed cafes": 1.5,
}


def _name_score(name: str) -> float:
    name_lower = name.lower()
    return sum(
        weight for kw, weight in _NAME_KEYWORDS.items() if kw in name_lower
    )


def _category_score(categories: list[str]) -> float:
    cats_lower = " | ".join(c.lower() for c in (categories or []))
    return sum(
        weight for kw, weight in _CATEGORY_KEYWORDS.items() if kw in cats_lower
    )


def curation_priority_score(cafe: dict) -> float:
    """
    Return a numeric curation priority score (higher = check this cafe first).

    Based entirely on existing metadata — no external calls, no scraping.
    This is a heuristic, not a recommendation quality score.
    """
    name = cafe.get("name", "")
    categories = cafe.get("categories") or []
    rating = float(cafe.get("rating") or 0)
    review_count = int(cafe.get("review_count") or 0)

    base = _name_score(name) + _category_score(categories)

    # Small popularity boost — well-reviewed cafes are worth verifying
    popularity_boost = min(2.0, review_count / 500) + min(1.5, (rating - 3.0) if rating >= 3 else 0)

    return round(base + popularity_boost, 3)


# ── Cafe fetch ────────────────────────────────────────────────────────────────

def fetch_cafes(region: str, source: str) -> list[dict]:
    """
    Fetch cafe records from the configured database. Never calls Yelp or any external API.

    source="local"      → uses DYNAMODB_ENDPOINT_URL (Docker)
    source="production" → uses real AWS (no endpoint override needed)
    """
    if _postgres_configured():
        if settings.database_environment not in {"local", "production"}:
            raise ValueError(
                "Set DATABASE_ENVIRONMENT=local or production before exporting."
            )
        if source != settings.database_environment:
            raise ValueError(
                f"--source {source} does not match "
                f"DATABASE_ENVIRONMENT={settings.database_environment}."
            )
    elif source == "production" and settings.dynamodb_endpoint_url:
        # Warn but allow — the user may have intentionally set endpoint to local
        print(
            "Warning: DYNAMODB_ENDPOINT_URL is set — 'production' source will read from "
            "local DynamoDB, not production. Unset DYNAMODB_ENDPOINT_URL to read from AWS.",
            file=sys.stderr,
        )

    cafes = db.scan_by_entity_type("CAFE")

    if region != "all":
        cafes = [c for c in cafes if c.get("region_key") == region]

    return cafes


# ── Filtering ─────────────────────────────────────────────────────────────────

def apply_filters(
    cafes: list[dict],
    min_rating: Optional[float],
    sort: str,
    limit: Optional[int],
) -> list[dict]:
    if min_rating is not None:
        cafes = [c for c in cafes if float(c.get("rating") or 0) >= min_rating]

    if sort == "rating":
        cafes.sort(key=lambda c: float(c.get("rating") or 0), reverse=True)
    elif sort == "review_count":
        cafes.sort(key=lambda c: int(c.get("review_count") or 0), reverse=True)
    else:  # "relevance" — curation priority
        cafes.sort(key=curation_priority_score, reverse=True)

    if limit:
        cafes = cafes[:limit]

    return cafes


# ── Output formatters ─────────────────────────────────────────────────────────

def _cafe_to_markdown_entry(cafe: dict, rank: int) -> str:
    priority = curation_priority_score(cafe)
    cats = ", ".join((cafe.get("categories") or [])[:4]) or "n/a"
    lines = [
        f"## {rank}. {cafe.get('name', 'Unknown')}",
        f"",
        f"- **cafe_id**: `{cafe.get('cafe_id', '?')}`",
        f"- **Region**: {cafe.get('region_label') or cafe.get('region_key') or 'n/a'}",
        f"- **Address**: {cafe.get('address') or cafe.get('location') or 'n/a'}",
        f"- **Yelp rating**: {cafe.get('rating') or 'n/a'} ({cafe.get('review_count') or 0} reviews)",
        f"- **Categories**: {cats}",
        f"- **Source/external_id**: {cafe.get('source') or 'n/a'} / {cafe.get('external_id') or 'n/a'}",
        f"- **Curation priority score**: {priority}",
    ]
    if cafe.get("external_url"):
        lines.append(f"- **Yelp URL**: {cafe['external_url']}")
    lines += [
        f"",
        f"### Verified drinks",
        f"",
        f"_Verify from official menu, personal visit, or cafe website only._",
        f"",
        f"| Drink name | Menu/source URL | Price | Milk options | Iced | Hot | Verification notes |",
        f"|---|---|---|---|---|---|---|",
        f"| | | | | | | |",
        f"",
    ]
    return "\n".join(lines)


def write_markdown(cafes: list[dict], output: Path, region: str, source: str) -> None:
    lines = [
        f"# Matcha Scout — Curation Checklist: {region.replace('-', ' ').title()}",
        f"",
        f"> **Local file — do not commit.** This file is gitignored.",
        f"> Verify drinks from official menus, personal visits, or cafe websites only.",
        f"> Yelp reviews are NOT valid sources for exact drink names or prices.",
        f"",
        f"- Source: {source} database",
        f"- Cafes: {len(cafes)}",
        f"- Sorted by curation priority (name/category keyword relevance + popularity)",
        f"",
        f"---",
        f"",
    ]
    for i, cafe in enumerate(cafes, start=1):
        lines.append(_cafe_to_markdown_entry(cafe, i))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(cafes)} cafes to {output}")


def write_json(cafes: list[dict], output: Path, region: str, source: str) -> None:
    payload = {
        "source": source,
        "region": region,
        "count": len(cafes),
        "note": "Local file — do not commit. Verify drinks from official menus only.",
        "cafes": [
            {
                "cafe_id": c.get("cafe_id"),
                "name": c.get("name"),
                "region_key": c.get("region_key"),
                "region_label": c.get("region_label"),
                "address": c.get("address") or c.get("location"),
                "rating": float(c["rating"]) if c.get("rating") else None,
                "review_count": int(c["review_count"]) if c.get("review_count") else None,
                "categories": c.get("categories"),
                "source": c.get("source"),
                "external_url": c.get("external_url"),
                "external_id": c.get("external_id"),
                "curation_priority_score": curation_priority_score(c),
                "verified_drinks": [],
            }
            for c in cafes
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(cafes)} cafes to {output}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a local curation checklist from cafe data (no Yelp calls, no DB writes)."
    )
    parser.add_argument("--region", default="all",
        help="Region to export: san-diego, orange-county, or all (default: all).")
    parser.add_argument("--source", default="local", choices=["local", "production"],
        help="Database environment to read from (default: local).")
    parser.add_argument("--output", required=True,
        help="Output file path (should end in .local.md or .local.json to stay gitignored).")
    parser.add_argument("--limit", type=int, default=None,
        help="Max cafes to include in output.")
    parser.add_argument("--sort", default="relevance",
        choices=["relevance", "rating", "review_count"],
        help="Sort order (default: relevance = curation priority heuristic).")
    parser.add_argument("--min-rating", type=float, default=None,
        help="Only include cafes at or above this Yelp rating.")
    parser.add_argument("--include-yelp-url", action="store_true", default=True,
        help="Include stored Yelp URLs when available. URLs are included by default.")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"],
        help="Output format (default: markdown).")
    return parser.parse_args()


def run(args: argparse.Namespace) -> int:
    output = Path(args.output)

    cafes = fetch_cafes(args.region, args.source)
    if not cafes:
        print(
            f"No cafes found for region={args.region!r} in the {args.source} database.",
            file=sys.stderr,
        )
        return 1

    cafes = apply_filters(cafes, args.min_rating, args.sort, args.limit)

    top_score = curation_priority_score(cafes[0]) if cafes else 0
    print(
        f"Fetched {len(cafes)} cafes | region={args.region!r} | "
        f"sort={args.sort!r} | top priority score={top_score}"
    )

    if args.format == "json":
        write_json(cafes, output, args.region, args.source)
    else:
        write_markdown(cafes, output, args.region, args.source)

    # Remind user to keep this file local
    if not (output.name.endswith(".local.md") or output.name.endswith(".local.json")
            or output.name.startswith("my-")):
        print(
            f"Warning: output file {output.name!r} may not match gitignore patterns.\n"
            "  Rename to *.local.md, *.local.json, or my-*.md to stay gitignored.",
            file=sys.stderr,
        )
    return 0


def main() -> None:
    args = parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
