"""
Manual drink curation script for Matcha Scout.

Reads a JSON curation file and creates admin-curated drinks under existing cafes.
Always defaults to dry-run. Local writes require --apply --local.
Production writes require --apply --production --confirm-production.

Usage:
    # Preview what would be created/skipped:
    python -m app.ingest.manual_drink_curation \\
        --file data/curation/san-diego-drinks.example.json --dry-run

    # Write to the local PostgreSQL database:
    python -m app.ingest.manual_drink_curation \\
        --file data/curation/my-san-diego-drinks.json --apply --local

    # Write to production Neon:
    python -m app.ingest.manual_drink_curation \\
        --file data/curation/my-san-diego-drinks.json \\
        --apply --production --confirm-production

Rules:
    - source is always set to "admin_curated"
    - verification_status from the file (default "admin_curated"); use "admin_verified"
      once a drink has been personally verified on-site
    - Taste profiles start neutral (3.0 all dims, review_count=0, confidence=unrated)
    - Yelp excerpt counts NEVER affect confidence
    - Existing drinks are skipped unless --allow-overwrite is given
    - Production writes require an explicit confirmation flag and no local endpoint
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services import db


def _postgres_configured() -> bool:
    value = getattr(settings, "database_url", None)
    return isinstance(value, str) and bool(value)


# ── Validation ────────────────────────────────────────────────────────────────

class CurationError(ValueError):
    pass


_PLACEHOLDER_TERMS = (
    "todo",
    "example",
    "placeholder",
    "unknown",
    "tbd",
    "fixme",
    "replace",
)


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _has_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(term in lowered for term in _PLACEHOLDER_TERMS)


def validate_drink_entry(entry: dict[str, Any], index: int) -> None:
    """Raise CurationError with a human-readable message if the entry is invalid."""
    label = f"Entry #{index} ({entry.get('name', 'no name')!r})"

    name = entry.get("name")
    if not name or not str(name).strip():
        raise CurationError(f"{label}: 'name' is required and cannot be empty.")
    if _has_placeholder(str(name)):
        raise CurationError(f"{label}: 'name' contains placeholder text.")
    if len(str(name).strip()) > 120:
        raise CurationError(f"{label}: 'name' exceeds 120 characters.")

    price = entry.get("price")
    if price is not None:
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise CurationError(f"{label}: 'price' must be a number, got {price!r}.")
        if p <= 0:
            raise CurationError(f"{label}: 'price' must be positive, got {p}.")

    milk_options = entry.get("milk_options")
    if milk_options is not None and not isinstance(milk_options, list):
        raise CurationError(f"{label}: 'milk_options' must be a list, got {type(milk_options).__name__}.")

    for bool_field in ("is_iced", "is_hot"):
        val = entry.get(bool_field)
        if val is not None and not isinstance(val, bool):
            raise CurationError(f"{label}: '{bool_field}' must be a boolean, got {val!r}.")

    has_external = entry.get("cafe_external_source") and entry.get("cafe_external_id")
    has_direct = entry.get("cafe_id")
    if not has_external and not has_direct:
        raise CurationError(
            f"{label}: must supply either (cafe_external_source + cafe_external_id) or cafe_id."
        )

    verification_source = entry.get("verification_source")
    verification_url = entry.get("verification_url")
    verification_notes = entry.get("verification_notes") or entry.get("curation_notes")
    if _is_blank(verification_source):
        raise CurationError(f"{label}: 'verification_source' is required.")
    if _has_placeholder(str(verification_source)):
        raise CurationError(f"{label}: 'verification_source' contains placeholder text.")
    if _is_blank(verification_url) and _is_blank(verification_notes):
        raise CurationError(
            f"{label}: provide at least one of 'verification_url' or 'verification_notes'."
        )
    for field_name, value in (
        ("verification_url", verification_url),
        ("verification_notes", verification_notes),
    ):
        if value is not None and _has_placeholder(str(value)):
            raise CurationError(f"{label}: '{field_name}' contains placeholder text.")


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized copy of a curation entry (does not mutate input)."""
    out = dict(entry)
    out["name"] = str(out["name"]).strip()
    if out.get("description"):
        out["description"] = str(out["description"]).strip()
    if out.get("milk_options"):
        out["milk_options"] = [m.lower().strip() for m in out["milk_options"] if str(m).strip()]
    else:
        out["milk_options"] = []
    out.setdefault("verification_status", "admin_curated")
    if out.get("verification_source"):
        out["verification_source"] = str(out["verification_source"]).strip()
    if out.get("verification_url"):
        out["verification_url"] = str(out["verification_url"]).strip()
    if out.get("verification_notes"):
        out["verification_notes"] = str(out["verification_notes"]).strip()
    return out


# ── Cafe resolution ───────────────────────────────────────────────────────────

def resolve_cafe(entry: dict[str, Any]) -> dict | None:
    """Return the configured database cafe item that matches this entry, or None."""
    if entry.get("cafe_external_source") and entry.get("cafe_external_id"):
        return db.find_cafe_by_external_id(
            entry["cafe_external_source"], entry["cafe_external_id"]
        )
    if entry.get("cafe_id"):
        return db.get_item(pk=f"CAFE#{entry['cafe_id']}", sk="METADATA")
    return None


# ── Per-entry processing ──────────────────────────────────────────────────────

@dataclass
class CurationResult:
    would_create: list[str] = field(default_factory=list)
    skipped_existing: list[str] = field(default_factory=list)
    missing_cafe: list[str] = field(default_factory=list)
    invalid_records: list[str] = field(default_factory=list)
    created: list[str] = field(default_factory=list)

    def print_summary(self, applying: bool) -> None:
        print("\n── Summary ───────────────────────────────────")
        if applying:
            print(f"  Created:          {len(self.created)}")
        else:
            print(f"  Would create:     {len(self.would_create)}")
        print(f"  Skipped existing: {len(self.skipped_existing)}")
        print(f"  Missing cafe:     {len(self.missing_cafe)}")
        print(f"  Invalid records:  {len(self.invalid_records)}")

        if self.missing_cafe:
            print("\n  Missing cafes (run Yelp ingestion first or fix cafe_id):")
            for m in self.missing_cafe:
                print(f"    - {m}")

        if self.invalid_records:
            print("\n  Invalid records:")
            for r in self.invalid_records:
                print(f"    - {r}")


def process_entry(
    entry: dict[str, Any],
    index: int,
    *,
    applying: bool,
    allow_overwrite: bool,
    now: str,
    result: CurationResult,
) -> None:
    label = f"#{index} {entry.get('name', '?')!r}"

    # Validate
    try:
        validate_drink_entry(entry, index)
    except CurationError as exc:
        print(f"  INVALID  {label}: {exc}")
        result.invalid_records.append(str(exc))
        return

    entry = normalize_entry(entry)

    # Resolve cafe
    cafe = resolve_cafe(entry)
    if not cafe:
        hint = entry.get("cafe_name_hint") or entry.get("cafe_id") or entry.get("cafe_external_id") or "?"
        msg = f"{label} — cafe not found (hint: {hint!r})"
        print(f"  NO CAFE  {msg}")
        result.missing_cafe.append(msg)
        return

    cafe_id: str = cafe["cafe_id"]
    cafe_name: str = cafe.get("name", cafe_id)

    # Check for existing drink
    existing = db.find_existing_drink_for_cafe(cafe_id, entry["name"])
    if existing and not allow_overwrite:
        msg = f"{label} at {cafe_name!r} — already exists ({existing['drink_id']}), skipping"
        print(f"  SKIP     {msg}")
        result.skipped_existing.append(msg)
        return

    # Report or apply
    price_str = f"${float(entry['price']):.2f}" if entry.get("price") is not None else "no price"
    print(f"  {'CREATE' if not applying else 'WRITE '}   {label} @ {cafe_name!r} ({price_str})")

    if not applying:
        result.would_create.append(f"{entry['name']} @ {cafe_name}")
        return

    drink_id = f"drink-{uuid.uuid4()}"
    drink_item: dict[str, Any] = {
        "drink_id": drink_id,
        "cafe_id": cafe_id,
        "name": entry["name"],
        "description": entry.get("description") or "",
        "price": Decimal(str(entry["price"])) if entry.get("price") is not None else Decimal("0"),
        "milk_options": entry.get("milk_options") or [],
        "source": "admin_curated",
        "verification_status": entry.get("verification_status", "admin_curated"),
        "verification_source": entry.get("verification_source") or "",
        "verification_url": entry.get("verification_url") or "",
        "verification_notes": entry.get("verification_notes") or entry.get("curation_notes") or "",
        "submitted_at": now,
        "created_at": now,
    }
    if entry.get("is_iced") is not None:
        drink_item["is_iced"] = entry["is_iced"]
    if entry.get("is_hot") is not None:
        drink_item["is_hot"] = entry["is_hot"]

    db.create_admin_curated_drink(cafe_id, drink_item)
    result.created.append(f"{entry['name']} @ {cafe_name} [{drink_id}]")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a manual drink curation JSON file to the local Matcha Scout database."
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to the curation JSON file (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview only — no writes. This is the default when --apply is not given.",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Write drinks to the database. Requires --local.",
    )
    parser.add_argument(
        "--local", action="store_true",
        help="Confirm this run targets the local database.",
    )
    parser.add_argument(
        "--production", action="store_true",
        help="Confirm this run targets the production database.",
    )
    parser.add_argument(
        "--confirm-production", action="store_true",
        help="Required with --apply --production to prevent accidental production writes.",
    )
    parser.add_argument(
        "--allow-overwrite", action="store_true",
        help="Re-create a drink even if one with the same name already exists at the cafe.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> int:
    applying = args.apply
    local = getattr(args, "local", False)
    production = getattr(args, "production", False)
    confirm_production = getattr(args, "confirm_production", False)

    if local and production:
        print("ERROR: Choose only one target: --local or --production.", file=sys.stderr)
        return 2

    if _postgres_configured():
        if local and settings.database_environment != "local":
            print(
                "ERROR: --local requires DATABASE_ENVIRONMENT=local.",
                file=sys.stderr,
            )
            return 2
        if production and settings.database_environment != "production":
            print(
                "ERROR: --production requires DATABASE_ENVIRONMENT=production.",
                file=sys.stderr,
            )
            return 2
    else:
        if local and not settings.dynamodb_endpoint_url:
            print(
                "ERROR: --local requires DYNAMODB_ENDPOINT_URL to be set.",
                file=sys.stderr,
            )
            return 2

        if production and settings.dynamodb_endpoint_url:
            print(
                "ERROR: --production refused because DYNAMODB_ENDPOINT_URL is set. "
                "Unset it before targeting production DynamoDB.",
                file=sys.stderr,
            )
            return 2

    if applying:
        if not local and not production:
            print(
                "ERROR: --apply requires either --local or --production.",
                file=sys.stderr,
            )
            return 2

        if production and not confirm_production:
            print(
                "ERROR: --apply --production requires --confirm-production.",
                file=sys.stderr,
            )
            return 2

    mode = "APPLY" if applying else "DRY RUN"

    # Load file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {file_path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict) or "drinks" not in payload:
        print("ERROR: Curation file must be a JSON object with a 'drinks' array.", file=sys.stderr)
        return 1

    drinks = payload["drinks"]
    if not isinstance(drinks, list):
        print("ERROR: 'drinks' must be a JSON array.", file=sys.stderr)
        return 1

    source_note = payload.get("source_note", "")
    print(f"{mode}: manual drink curation from {file_path}")
    if source_note:
        print(f"  Note: {source_note}")
    print(f"  Entries: {len(drinks)}")
    print()

    now = datetime.now(timezone.utc).isoformat()
    result = CurationResult()

    for i, entry in enumerate(drinks, start=1):
        if not isinstance(entry, dict):
            msg = f"Entry #{i} is not a JSON object"
            print(f"  INVALID  {msg}")
            result.invalid_records.append(msg)
            continue
        process_entry(
            entry, i,
            applying=applying,
            allow_overwrite=args.allow_overwrite,
            now=now,
            result=result,
        )

    result.print_summary(applying)

    if not applying:
        print("\nDry run only. Re-run with --apply --local to write to the local database.")

    # Exit non-zero if any records were invalid or cafes were missing
    if result.invalid_records or result.missing_cafe:
        return 1
    return 0


def main() -> None:
    args = parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
