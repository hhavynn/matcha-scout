"""Plan and safely apply the audited Deep Research reconciliation.

Dry-run is the default. Local writes require --apply --local. Production writes
require --apply --production --confirm-production plus an exact confirmation.
Every apply writes and verifies a backup before the first database mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings
from app.services import db


EXACT_PRODUCTION_CONFIRMATION = "APPLY MATCHA SCOUT DEEP RESEARCH TO PRODUCTION"
EXPECTED_PRODUCTION = {
    "cafes_matched": 44,
    "cafes_created": 0,
    "cafes_updated": 13,
    "drinks_created": 10,
    "drinks_updated": 18,
    "drinks_soft_excluded": 2,
}

_ROOT_CANDIDATES = [
    Path(__file__).resolve().parents[3],
    Path(__file__).resolve().parents[2],
]
REPO_ROOT = next(
    (root for root in _ROOT_CANDIDATES if (root / "data/research").exists()),
    _ROOT_CANDIDATES[0],
)
DEFAULT_CAFES = REPO_ROOT / "data/research/sd-matcha-cafes-2026-06-24.json"
DEFAULT_DRINKS = REPO_ROOT / "data/research/sd-matcha-verified-drinks-2026-06-24.json"
DEFAULT_BACKUP_DIR = REPO_ROOT / "data/backups"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = normalized.replace("’", "'").replace("&", " and ")
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(
        "".join(char if char.isalnum() else " " for char in normalized.casefold()).split()
    )


def deterministic_drink_id(cafe_id: str, drink_name: str) -> str:
    digest = hashlib.sha1(
        f"{cafe_id}:{normalize_name(drink_name)}".encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()[:16]
    return f"drink-research-{digest}"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return payload


def json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def values_equal(left: Any, right: Any) -> bool:
    numeric = (int, float, Decimal)
    if (
        isinstance(left, numeric)
        and not isinstance(left, bool)
        and isinstance(right, numeric)
        and not isinstance(right, bool)
    ):
        return Decimal(str(left)) == Decimal(str(right))
    return left == right


def database_host(database_url: str | None = None) -> str:
    value = database_url if database_url is not None else settings.database_url
    if not value:
        return "(not configured)"
    try:
        return urlparse(value).hostname or "(unknown host)"
    except ValueError:
        return "(invalid URL)"


def host_appears_local(host: str) -> bool:
    normalized = host.casefold().strip("[]")
    return (
        normalized in {"localhost", "127.0.0.1", "::1", "postgres", "matcha-postgres"}
        or normalized.endswith(".local")
        or normalized.startswith("192.168.")
        or normalized.startswith("10.")
    )


def resolve_cafe(entry: dict[str, Any], cafes: list[dict[str, Any]]) -> tuple[dict | None, str]:
    if entry.get("cafe_id"):
        matches = [cafe for cafe in cafes if cafe.get("cafe_id") == entry["cafe_id"]]
        if len(matches) == 1:
            cafe = matches[0]
            expected_address = normalize_name(entry.get("address", ""))
            actual_address = normalize_name(cafe.get("address", ""))
            if expected_address and expected_address != actual_address:
                return None, "address_conflict"
            return cafe, "internal_id"

    candidates = {
        normalize_name(name)
        for name in [entry["name"], *(entry.get("aliases") or [])]
        if name
    }
    exact = [
        cafe
        for cafe in cafes
        if normalize_name(cafe.get("name", "")) in candidates
    ]
    if len(exact) == 1:
        return exact[0], "exact_name"
    if len(exact) > 1:
        return None, "ambiguous_name"
    return None, "missing"


def match_drink(entry: dict[str, Any], drinks: list[dict[str, Any]]) -> dict | None:
    candidates = {
        normalize_name(name)
        for name in [entry["name"], *(entry.get("aliases") or [])]
        if name
    }
    matches = [
        drink
        for drink in drinks
        if normalize_name(drink.get("name", "")) in candidates
    ]
    return matches[0] if len(matches) == 1 else None


def merged_item(item: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(item)
    merged.update(updates)
    return merged


def drink_updates(entry: dict[str, Any]) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "name": entry["name"],
        "description": entry.get("description") or "",
        "price": Decimal(str(entry["price"])) if entry.get("price") is not None else None,
        "milk_options": entry.get("milk_options") or [],
        "source": "admin_curated",
        "verification_status": entry.get("verification_status", "admin_verified"),
        "verification_source": entry["verification_source"],
        "verification_url": entry.get("verification_url") or "",
        "verification_notes": entry.get("verification_notes") or "",
        "verified_at": entry.get("verified_at"),
    }
    if entry.get("is_iced") is not None:
        updates["is_iced"] = entry["is_iced"]
    if entry.get("is_hot") is not None:
        updates["is_hot"] = entry["is_hot"]
    return updates


@dataclass
class ReconciliationPlan:
    target: str
    database_environment: str
    database_host: str
    generated_at: str
    operations: list[dict[str, Any]]
    blocked: list[dict[str, Any]]
    matches: list[dict[str, Any]]
    counts: dict[str, int]
    expected_drift: dict[str, dict[str, int]]
    risk_level: str

    def as_dict(self) -> dict[str, Any]:
        return json_safe({
            "version": 1,
            "target": self.target,
            "database_environment": self.database_environment,
            "database_host": self.database_host,
            "generated_at": self.generated_at,
            "operations": self.operations,
            "blocked": self.blocked,
            "matches": self.matches,
            "counts": self.counts,
            "expected_production_counts": EXPECTED_PRODUCTION,
            "expected_drift": self.expected_drift,
            "risk_level": self.risk_level,
            "imports_taste_profiles": False,
            "imports_external_ratings": False,
            "creates_cafes": False,
        })


def build_plan(
    cafe_payload: dict[str, Any],
    drink_payload: dict[str, Any],
    *,
    target: str,
    remove_excluded: bool,
) -> ReconciliationPlan:
    cafes = db.scan_by_entity_type("CAFE")
    operations: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    matches: list[dict[str, Any]] = []

    for entry in cafe_payload["cafes"]:
        cafe, strategy = resolve_cafe(entry, cafes)
        matches.append({
            "report_name": entry["name"],
            "classification": entry["classification"],
            "strategy": strategy,
            "cafe_id": cafe.get("cafe_id") if cafe else None,
            "database_name": cafe.get("name") if cafe else None,
        })
        if not cafe:
            blocked.append({
                "kind": "cafe_match",
                "name": entry["name"],
                "reason": strategy,
            })
            continue
        updates = entry.get("updates") or {}
        after = merged_item(cafe, updates)
        if any(not values_equal(cafe.get(key), value) for key, value in updates.items()):
            operations.append({
                "action": "update_cafe",
                "entity": "cafe",
                "entity_id": cafe["cafe_id"],
                "pk": cafe["PK"],
                "sk": cafe["SK"],
                "before": cafe,
                "after": after,
                "changed_fields": sorted(updates),
            })

    drinks_by_cafe: dict[str, list[dict[str, Any]]] = {}
    for entry in drink_payload["drinks"]:
        cafe_id = entry["cafe_id"]
        cafe = next((item for item in cafes if item.get("cafe_id") == cafe_id), None)
        if not cafe:
            blocked.append({
                "kind": "missing_cafe",
                "name": entry["name"],
                "cafe_id": cafe_id,
            })
            continue
        drinks = drinks_by_cafe.setdefault(
            cafe_id,
            [
                item
                for item in db.query_gsi(f"CAFE#{cafe_id}")
                if item.get("SK") == "METADATA"
            ],
        )
        existing = match_drink(entry, drinks)
        updates = drink_updates(entry)
        if existing:
            if existing.get("source") != "admin_curated":
                blocked.append({
                    "kind": "user_drink_name_collision",
                    "name": entry["name"],
                    "drink_id": existing["drink_id"],
                    "source": existing.get("source"),
                })
                continue
            after = merged_item(existing, updates)
            if entry.get("is_iced") is None:
                after.pop("is_iced", None)
            if entry.get("is_hot") is None:
                after.pop("is_hot", None)
            if after != existing:
                operations.append({
                    "action": "update_drink",
                    "entity": "drink",
                    "entity_id": existing["drink_id"],
                    "cafe_id": cafe_id,
                    "pk": existing["PK"],
                    "sk": existing["SK"],
                    "before": existing,
                    "after": after,
                    "changed_fields": sorted(
                        key for key in set(existing) | set(after)
                        if not values_equal(existing.get(key), after.get(key))
                    ),
                })
            continue

        drink_id = deterministic_drink_id(cafe_id, entry["name"])
        collision = db.get_item(f"DRINK#{drink_id}", "METADATA")
        if collision:
            blocked.append({
                "kind": "drink_id_collision",
                "name": entry["name"],
                "drink_id": drink_id,
            })
            continue
        now = utc_now()
        metadata = {
            **updates,
            "PK": f"DRINK#{drink_id}",
            "SK": "METADATA",
            "GSI1PK": f"CAFE#{cafe_id}",
            "GSI1SK": f"DRINK#{drink_id}",
            "drink_id": drink_id,
            "cafe_id": cafe_id,
            "created_at": now,
            "submitted_at": now,
        }
        operations.append({
            "action": "create_drink",
            "entity": "drink",
            "entity_id": drink_id,
            "cafe_id": cafe_id,
            "pk": metadata["PK"],
            "sk": metadata["SK"],
            "before": None,
            "after": metadata,
            "changed_fields": sorted(metadata),
        })
        drinks.append(metadata)

    if remove_excluded:
        for entry in drink_payload.get("excluded_drinks", []):
            if entry.get("classification") != "excluded":
                continue
            cafe_id = entry["cafe_id"]
            drinks = drinks_by_cafe.setdefault(
                cafe_id,
                [
                    item
                    for item in db.query_gsi(f"CAFE#{cafe_id}")
                    if item.get("SK") == "METADATA"
                ],
            )
            existing = match_drink(entry, drinks)
            if not existing:
                continue
            partition = db.query_by_pk(f"DRINK#{existing['drink_id']}")
            reviews = [
                item for item in partition
                if item.get("SK", "").startswith("REVIEW#")
            ]
            profile = next(
                (item for item in partition if item.get("SK") == "TASTE_PROFILE"),
                None,
            )
            review_count = int((profile or {}).get("review_count", 0))
            if existing.get("source") != "admin_curated":
                blocked.append({
                    "kind": "excluded_user_drink",
                    "name": entry["name"],
                    "drink_id": existing["drink_id"],
                })
                continue
            if reviews or review_count > 0:
                blocked.append({
                    "kind": "excluded_reviewed_drink",
                    "name": entry["name"],
                    "drink_id": existing["drink_id"],
                    "review_items": len(reviews),
                    "profile_review_count": review_count,
                })
                continue

            if target == "production":
                after = merged_item(existing, {
                    "catalog_status": "excluded",
                    "exclusion_reason": entry["reason"],
                    "excluded_at": utc_now(),
                })
                operations.append({
                    "action": "soft_exclude_drink",
                    "entity": "drink",
                    "entity_id": existing["drink_id"],
                    "cafe_id": cafe_id,
                    "pk": existing["PK"],
                    "sk": existing["SK"],
                    "before": existing,
                    "after": after,
                    "changed_fields": ["catalog_status", "excluded_at", "exclusion_reason"],
                })
            else:
                operations.append({
                    "action": "delete_unreviewed_admin_drink",
                    "entity": "drink",
                    "entity_id": existing["drink_id"],
                    "cafe_id": cafe_id,
                    "pk": existing["PK"],
                    "sk": existing["SK"],
                    "before": existing,
                    "after": None,
                    "changed_fields": [],
                })

    counts = {
        "cafes_matched": sum(1 for match in matches if match["cafe_id"]),
        "cafes_created": 0,
        "cafes_updated": sum(op["action"] == "update_cafe" for op in operations),
        "drinks_created": sum(op["action"] == "create_drink" for op in operations),
        "drinks_updated": sum(op["action"] == "update_drink" for op in operations),
        "drinks_soft_excluded": sum(op["action"] == "soft_exclude_drink" for op in operations),
        "drinks_deleted_local": sum(
            op["action"] == "delete_unreviewed_admin_drink" for op in operations
        ),
        "blocked": len(blocked),
    }
    drift = {}
    if target == "production":
        drift = {
            key: {"expected": expected, "actual": counts.get(key, 0)}
            for key, expected in EXPECTED_PRODUCTION.items()
            if counts.get(key, 0) != expected
        }
    risk_level = "high" if blocked else ("medium" if target == "production" and drift else "low")
    return ReconciliationPlan(
        target=target,
        database_environment=settings.database_environment,
        database_host=database_host(),
        generated_at=utc_now(),
        operations=operations,
        blocked=blocked,
        matches=matches,
        counts=counts,
        expected_drift=drift,
        risk_level=risk_level,
    )


def affected_partitions(plan: ReconciliationPlan) -> dict[str, list[dict[str, Any]]]:
    partitions: dict[str, list[dict[str, Any]]] = {}
    for operation in plan.operations:
        pk = operation["pk"]
        if pk not in partitions:
            partitions[pk] = db.query_by_pk(pk)
    return partitions


def write_json_verified(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2) + "\n", encoding="utf-8")
    reread = json.loads(path.read_text(encoding="utf-8"))
    if reread.get("version") != payload.get("version"):
        raise RuntimeError(f"Backup verification failed for {path}.")
    return path


def write_backup(plan: ReconciliationPlan, backup_dir: Path) -> Path:
    backup_path = backup_dir / f"deep-research-{plan.target}-{timestamp_slug()}.json"
    payload = {
        "version": 1,
        "kind": "matcha_scout_deep_research_backup",
        "created_at": utc_now(),
        "target": plan.target,
        "database_environment": plan.database_environment,
        "database_host": plan.database_host,
        "plan": plan.as_dict(),
        "partitions_before": affected_partitions(plan),
    }
    return write_json_verified(backup_path, payload)


def write_report(
    plan: ReconciliationPlan,
    path: Path,
    *,
    applied: bool,
    backup: str | None,
    status: str = "completed",
    error: str | None = None,
) -> Path:
    payload = {
        "version": 1,
        "kind": "matcha_scout_deep_research_reconciliation",
        "completed_at": utc_now(),
        "applied": applied,
        "status": status,
        "error": error,
        "backup_path": backup,
        "plan": plan.as_dict(),
    }
    return write_json_verified(path, payload)


def apply_plan(plan: ReconciliationPlan) -> None:
    for operation in plan.operations:
        action = operation["action"]
        if action in {"update_cafe", "update_drink", "soft_exclude_drink"}:
            db.put_item(operation["after"])
        elif action == "create_drink":
            after = operation["after"]
            db.create_admin_curated_drink(after["cafe_id"], after)
        elif action == "delete_unreviewed_admin_drink":
            partition = db.query_by_pk(operation["pk"])
            reviews = [
                item for item in partition
                if item.get("SK", "").startswith("REVIEW#")
            ]
            profile = next(
                (item for item in partition if item.get("SK") == "TASTE_PROFILE"),
                {},
            )
            if reviews or int(profile.get("review_count", 0)) > 0:
                raise RuntimeError(
                    f"Deletion safety changed for {operation['entity_id']}; aborting."
                )
            db.delete_partition(operation["pk"])
        else:
            raise RuntimeError(f"Unsupported operation: {action}")


def validate_target(args: argparse.Namespace) -> str:
    target = "production" if args.production else "local"
    if args.local and args.production:
        raise SystemExit("Choose only one target: --local or --production.")
    if args.apply and not (args.local or args.production):
        raise SystemExit("--apply requires --local or --production.")
    if args.production and settings.database_environment != "production":
        raise SystemExit("Production target requires DATABASE_ENVIRONMENT=production.")
    if args.local and settings.database_environment != "local":
        raise SystemExit("Local target requires DATABASE_ENVIRONMENT=local.")

    host = database_host()
    if args.production and host_appears_local(host):
        raise SystemExit(f"Production target refused for local-looking database host: {host}")
    if args.production and (not settings.database_url or "neon.tech" not in host):
        raise SystemExit("Production target requires a Neon DATABASE_URL.")
    if args.local and settings.database_url and not host_appears_local(host):
        raise SystemExit(f"Local target refused for non-local database host: {host}")
    return target


def confirm_production(args: argparse.Namespace) -> None:
    if not (args.apply and args.production):
        return
    if not args.confirm_production:
        raise SystemExit("Production apply requires --confirm-production.")
    supplied = args.confirmation
    if supplied is None:
        if not sys.stdin.isatty():
            raise SystemExit(
                "Non-interactive production apply requires "
                f"--confirmation {EXACT_PRODUCTION_CONFIRMATION!r}."
            )
        supplied = input(
            f"Type exactly {EXACT_PRODUCTION_CONFIRMATION!r} to continue: "
        )
    if supplied != EXACT_PRODUCTION_CONFIRMATION:
        raise SystemExit("Production confirmation did not match exactly.")


def print_plan(plan: ReconciliationPlan) -> None:
    print(f"Target environment: {plan.database_environment or '(unset)'}")
    print(f"Database host: {plan.database_host}")
    print(f"Risk level: {plan.risk_level}")
    print("Operation counts:")
    for key, value in plan.counts.items():
        print(f"  {key}: {value}")
    if plan.expected_drift:
        print("Expected production drift:")
        for key, values in plan.expected_drift.items():
            print(f"  {key}: expected {values['expected']}, actual {values['actual']}")
    if plan.blocked:
        print("Blocked operations:")
        for item in plan.blocked:
            print(f"  {item['kind']}: {item.get('name') or item.get('drink_id')}")
    print("Planned writes:")
    for operation in plan.operations:
        print(f"  {operation['action']}: {operation['entity_id']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cafes", type=Path, default=DEFAULT_CAFES)
    parser.add_argument("--drinks", type=Path, default=DEFAULT_DRINKS)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--confirm-production", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument("--remove-excluded", action="store_true")
    parser.add_argument("--write-backup", action="store_true")
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument("--report-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = validate_target(args)
    print("APPLY" if args.apply else "DRY RUN")
    plan = build_plan(
        load_json(args.cafes),
        load_json(args.drinks),
        target=target,
        remove_excluded=args.remove_excluded,
    )
    print_plan(plan)

    default_report = args.backup_dir / (
        f"reconciliation-{target}-{timestamp_slug()}.json"
    )
    report_path = args.report_output or (default_report if args.production else None)

    if plan.blocked:
        if report_path:
            write_report(plan, report_path, applied=False, backup=None)
        return 1
    if args.production and plan.expected_drift:
        if report_path:
            write_report(plan, report_path, applied=False, backup=None)
        print("Production plan differs from the approved expected counts; refusing apply.")
        return 2 if args.apply else 0

    backup_path: Path | None = None
    if args.write_backup or args.apply:
        backup_path = write_backup(plan, args.backup_dir)
        print(f"Verified backup: {backup_path}")

    if args.apply:
        confirm_production(args)
        try:
            apply_plan(plan)
        except Exception as exc:
            failure_report = report_path or (
                args.backup_dir / f"reconciliation-{target}-failed-{timestamp_slug()}.json"
            )
            write_report(
                plan,
                failure_report,
                applied=False,
                backup=str(backup_path) if backup_path else None,
                status="partial_failure",
                error=f"{type(exc).__name__}: {exc}",
            )
            print(f"Apply failed; reconciliation report: {failure_report}", file=sys.stderr)
            return 1
        print("Apply completed.")

    if report_path:
        written = write_report(
            plan,
            report_path,
            applied=args.apply,
            backup=str(backup_path) if backup_path else None,
        )
        print(f"Reconciliation report: {written}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
