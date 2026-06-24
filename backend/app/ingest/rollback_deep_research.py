"""Safely roll back one Deep Research sync from its verified backup."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.core.config import settings
from app.ingest.sync_deep_research import (
    EXACT_PRODUCTION_CONFIRMATION,
    database_host,
    host_appears_local,
    json_safe,
    values_equal,
)
from app.services import db


EXACT_ROLLBACK_CONFIRMATION = "ROLL BACK MATCHA SCOUT DEEP RESEARCH PRODUCTION"


def load_backup(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("kind") != "matcha_scout_deep_research_backup":
        raise SystemExit("The supplied file is not a Deep Research backup.")
    if not isinstance(payload.get("partitions_before"), dict):
        raise SystemExit("Backup is missing partitions_before.")
    return payload


def validate_target(args: argparse.Namespace, backup: dict) -> str:
    target = "production" if args.production else "local"
    if args.local and args.production:
        raise SystemExit("Choose only one target.")
    if args.apply and not (args.local or args.production):
        raise SystemExit("--apply requires --local or --production.")
    if backup.get("target") != target:
        raise SystemExit("Backup target does not match requested rollback target.")
    if settings.database_environment != target:
        raise SystemExit(f"Rollback requires DATABASE_ENVIRONMENT={target}.")
    host = database_host()
    if host != backup.get("database_host"):
        raise SystemExit(
            f"Backup host {backup.get('database_host')} does not match current host {host}."
        )
    if target == "production" and host_appears_local(host):
        raise SystemExit("Production rollback refused for a local-looking host.")
    return target


def build_rollback_plan(backup: dict) -> tuple[list[dict], list[dict]]:
    operations = []
    blocked = []
    for original in reversed(backup["plan"]["operations"]):
        action = original["action"]
        pk = original["pk"]
        current_partition = db.query_by_pk(pk)
        current_metadata = next(
            (item for item in current_partition if item.get("SK") == "METADATA"),
            None,
        )
        if action == "create_drink":
            reviews = [
                item for item in current_partition
                if item.get("SK", "").startswith("REVIEW#")
            ]
            profile = next(
                (item for item in current_partition if item.get("SK") == "TASTE_PROFILE"),
                {},
            )
            if reviews or int(profile.get("review_count", 0)) > 0:
                blocked.append({
                    "entity_id": original["entity_id"],
                    "reason": "new drink has Matcha Scout reviews",
                })
                continue
            if current_metadata and current_metadata != original["after"]:
                blocked.append({
                    "entity_id": original["entity_id"],
                    "reason": "new drink metadata changed after sync",
                })
                continue
            operations.append({
                "action": "remove_created_drink",
                "entity_id": original["entity_id"],
                "pk": pk,
            })
            continue

        before = original.get("before")
        after = original.get("after")
        if action == "delete_unreviewed_admin_drink":
            if current_partition:
                blocked.append({
                    "entity_id": original["entity_id"],
                    "reason": "deleted partition has been recreated",
                })
                continue
            operations.append({
                "action": "restore_partition",
                "entity_id": original["entity_id"],
                "items": backup["partitions_before"].get(pk, []),
            })
            continue

        if current_metadata is None:
            blocked.append({
                "entity_id": original["entity_id"],
                "reason": "metadata is missing",
            })
            continue
        if after and current_metadata != after:
            blocked.append({
                "entity_id": original["entity_id"],
                "reason": "metadata changed after sync",
            })
            continue
        operations.append({
            "action": "restore_metadata",
            "entity_id": original["entity_id"],
            "item": before,
        })
    return operations, blocked


def confirm(args: argparse.Namespace, target: str) -> None:
    if not args.apply:
        return
    expected = (
        EXACT_ROLLBACK_CONFIRMATION if target == "production"
        else "ROLL BACK MATCHA SCOUT DEEP RESEARCH LOCAL"
    )
    if target == "production" and not args.confirm_production:
        raise SystemExit("Production rollback requires --confirm-production.")
    supplied = args.confirmation
    if supplied is None:
        if not sys.stdin.isatty():
            raise SystemExit(f"Non-interactive rollback requires --confirmation {expected!r}.")
        supplied = input(f"Type exactly {expected!r} to continue: ")
    if supplied != expected:
        raise SystemExit("Rollback confirmation did not match exactly.")


def apply_rollback(operations: list[dict]) -> None:
    for operation in operations:
        if operation["action"] == "restore_metadata":
            db.put_item(operation["item"])
        elif operation["action"] == "restore_partition":
            for item in operation["items"]:
                db.put_item(item)
        elif operation["action"] == "remove_created_drink":
            partition = db.query_by_pk(operation["pk"])
            reviews = [
                item for item in partition
                if item.get("SK", "").startswith("REVIEW#")
            ]
            if reviews:
                raise RuntimeError("A review appeared after rollback planning; aborting.")
            db.delete_partition(operation["pk"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--confirm-production", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument("--report-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backup = load_backup(args.backup)
    target = validate_target(args, backup)
    operations, blocked = build_rollback_plan(backup)
    print(f"Target environment: {settings.database_environment}")
    print(f"Database host: {database_host()}")
    print(f"Rollback operations: {len(operations)}")
    print(f"Blocked operations: {len(blocked)}")
    for item in blocked:
        print(f"  BLOCKED {item['entity_id']}: {item['reason']}")

    if args.report_output:
        args.report_output.parent.mkdir(parents=True, exist_ok=True)
        args.report_output.write_text(
            json.dumps(json_safe({
                "version": 1,
                "kind": "matcha_scout_deep_research_rollback_plan",
                "target": target,
                "operations": operations,
                "blocked": blocked,
            }), indent=2) + "\n",
            encoding="utf-8",
        )
    if blocked:
        return 1
    confirm(args, target)
    if args.apply:
        apply_rollback(operations)
        print("Rollback completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
