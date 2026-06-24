from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from app.ingest import rollback_deep_research as rollback
from app.ingest import sync_deep_research as sync


def args(**overrides):
    values = {
        "apply": False,
        "local": False,
        "production": False,
        "confirm_production": False,
        "confirmation": None,
    }
    values.update(overrides)
    return Namespace(**values)


def test_database_host_never_contains_credentials():
    url = "postgresql://user:super-secret@ep-example.neon.tech/neondb?sslmode=require"
    assert sync.database_host(url) == "ep-example.neon.tech"
    assert "secret" not in sync.database_host(url)


@pytest.mark.parametrize(
    "host",
    ["localhost", "127.0.0.1", "::1", "postgres", "matcha-postgres", "10.0.0.5"],
)
def test_local_host_detection(host):
    assert sync.host_appears_local(host)


def test_production_apply_requires_production_environment(monkeypatch):
    monkeypatch.setattr(sync.settings, "database_environment", "local")
    monkeypatch.setattr(
        sync.settings,
        "database_url",
        "postgresql://user:password@ep-example.neon.tech/neondb",
    )
    with pytest.raises(SystemExit, match="DATABASE_ENVIRONMENT=production"):
        sync.validate_target(args(apply=True, production=True))


def test_production_refuses_local_database(monkeypatch):
    monkeypatch.setattr(sync.settings, "database_environment", "production")
    monkeypatch.setattr(
        sync.settings,
        "database_url",
        "postgresql://matcha:matcha@localhost:5432/matcha_scout",
    )
    with pytest.raises(SystemExit, match="local-looking"):
        sync.validate_target(args(apply=True, production=True))


def test_production_apply_requires_exact_noninteractive_confirmation(monkeypatch):
    monkeypatch.setattr(sync.sys.stdin, "isatty", lambda: False)
    with pytest.raises(SystemExit, match="Non-interactive"):
        sync.confirm_production(
            args(
                apply=True,
                production=True,
                confirm_production=True,
                confirmation=None,
            )
        )
    with pytest.raises(SystemExit, match="did not match"):
        sync.confirm_production(
            args(
                apply=True,
                production=True,
                confirm_production=True,
                confirmation="yes",
            )
        )
    sync.confirm_production(
        args(
            apply=True,
            production=True,
            confirm_production=True,
            confirmation=sync.EXACT_PRODUCTION_CONFIRMATION,
        )
    )


def test_reviewed_excluded_drink_is_blocked_not_deleted(monkeypatch):
    cafe = {
        "PK": "CAFE#cafe-1",
        "SK": "METADATA",
        "cafe_id": "cafe-1",
        "name": "Cafe",
        "address": "1 Main St",
    }
    drink = {
        "PK": "DRINK#drink-1",
        "SK": "METADATA",
        "GSI1PK": "CAFE#cafe-1",
        "GSI1SK": "DRINK#drink-1",
        "drink_id": "drink-1",
        "cafe_id": "cafe-1",
        "name": "Seasonal Matcha",
        "source": "admin_curated",
    }
    review = {
        "PK": "DRINK#drink-1",
        "SK": "REVIEW#2026-01-01#1",
        "drink_id": "drink-1",
    }
    profile = {
        "PK": "DRINK#drink-1",
        "SK": "TASTE_PROFILE",
        "drink_id": "drink-1",
        "review_count": 1,
    }
    monkeypatch.setattr(sync.db, "scan_by_entity_type", lambda entity: [cafe] if entity == "CAFE" else [])
    monkeypatch.setattr(sync.db, "query_gsi", lambda value: [drink])
    monkeypatch.setattr(sync.db, "query_by_pk", lambda pk: [drink, review, profile])

    plan = sync.build_plan(
        {"cafes": [{"name": "Cafe", "cafe_id": "cafe-1", "address": "1 Main St", "classification": "verified"}]},
        {
            "drinks": [],
            "excluded_drinks": [{
                "name": "Seasonal Matcha",
                "cafe_id": "cafe-1",
                "cafe_name": "Cafe",
                "classification": "excluded",
                "reason": "No longer current",
            }],
        },
        target="production",
        remove_excluded=True,
    )

    assert not any(op["action"] == "soft_exclude_drink" for op in plan.operations)
    assert plan.blocked[0]["kind"] == "excluded_reviewed_drink"


def test_production_exclusion_is_soft(monkeypatch):
    cafe = {
        "PK": "CAFE#cafe-1", "SK": "METADATA", "cafe_id": "cafe-1",
        "name": "Cafe", "address": "1 Main St",
    }
    drink = {
        "PK": "DRINK#drink-1", "SK": "METADATA",
        "GSI1PK": "CAFE#cafe-1", "GSI1SK": "DRINK#drink-1",
        "drink_id": "drink-1", "cafe_id": "cafe-1",
        "name": "Seasonal Matcha", "source": "admin_curated",
    }
    profile = {
        "PK": "DRINK#drink-1", "SK": "TASTE_PROFILE",
        "drink_id": "drink-1", "review_count": 0,
    }
    monkeypatch.setattr(sync.db, "scan_by_entity_type", lambda entity: [cafe] if entity == "CAFE" else [])
    monkeypatch.setattr(sync.db, "query_gsi", lambda value: [drink])
    monkeypatch.setattr(sync.db, "query_by_pk", lambda pk: [drink, profile])

    plan = sync.build_plan(
        {"cafes": [{"name": "Cafe", "cafe_id": "cafe-1", "address": "1 Main St", "classification": "verified"}]},
        {
            "drinks": [],
            "excluded_drinks": [{
                "name": "Seasonal Matcha",
                "cafe_id": "cafe-1",
                "cafe_name": "Cafe",
                "classification": "excluded",
                "reason": "No longer current",
            }],
        },
        target="production",
        remove_excluded=True,
    )

    operation = next(op for op in plan.operations if op["action"] == "soft_exclude_drink")
    assert operation["after"]["catalog_status"] == "excluded"
    assert plan.counts["drinks_soft_excluded"] == 1


def test_apply_updates_metadata_without_touching_taste_profile():
    operation = {
        "action": "update_drink",
        "entity_id": "drink-1",
        "after": {"PK": "DRINK#drink-1", "SK": "METADATA", "drink_id": "drink-1"},
    }
    plan = sync.ReconciliationPlan(
        target="production",
        database_environment="production",
        database_host="ep-example.neon.tech",
        generated_at="2026-06-24T00:00:00Z",
        operations=[operation],
        blocked=[],
        matches=[],
        counts={},
        expected_drift={},
        risk_level="low",
    )
    with patch.object(sync.db, "put_item") as put_item:
        sync.apply_plan(plan)
    put_item.assert_called_once_with(operation["after"])
    assert put_item.call_args.args[0]["SK"] == "METADATA"


def test_existing_user_submitted_drink_is_never_overwritten(monkeypatch):
    cafe = {
        "PK": "CAFE#cafe-1", "SK": "METADATA", "cafe_id": "cafe-1",
        "name": "Cafe", "address": "1 Main St",
    }
    drink = {
        "PK": "DRINK#drink-user", "SK": "METADATA",
        "GSI1PK": "CAFE#cafe-1", "GSI1SK": "DRINK#drink-user",
        "drink_id": "drink-user", "cafe_id": "cafe-1",
        "name": "Matcha Latte", "source": "user_submitted",
    }
    monkeypatch.setattr(sync.db, "scan_by_entity_type", lambda entity: [cafe] if entity == "CAFE" else [])
    monkeypatch.setattr(sync.db, "query_gsi", lambda value: [drink])
    monkeypatch.setattr(sync.db, "get_item", lambda pk, sk: None)
    plan = sync.build_plan(
        {"cafes": [{"name": "Cafe", "cafe_id": "cafe-1", "address": "1 Main St", "classification": "verified"}]},
        {"drinks": [{
            "cafe_id": "cafe-1",
            "name": "Matcha Latte",
            "verification_source": "official_menu",
            "verification_url": "https://example.com/menu",
        }]},
        target="production",
        remove_excluded=False,
    )
    assert plan.blocked[0]["kind"] == "user_drink_name_collision"
    assert not any(op["action"] == "update_drink" for op in plan.operations)


def test_backup_contains_full_affected_partition(tmp_path):
    metadata = {"PK": "DRINK#drink-1", "SK": "METADATA", "drink_id": "drink-1"}
    profile = {"PK": "DRINK#drink-1", "SK": "TASTE_PROFILE", "review_count": 2}
    review = {"PK": "DRINK#drink-1", "SK": "REVIEW#1", "review_id": "review-1"}
    plan = sync.ReconciliationPlan(
        target="production",
        database_environment="production",
        database_host="ep-example.neon.tech",
        generated_at="2026-06-24T00:00:00Z",
        operations=[{
            "action": "update_drink",
            "entity_id": "drink-1",
            "pk": "DRINK#drink-1",
            "sk": "METADATA",
            "before": metadata,
            "after": metadata,
        }],
        blocked=[],
        matches=[],
        counts={},
        expected_drift={},
        risk_level="low",
    )
    with patch.object(sync.db, "query_by_pk", return_value=[metadata, profile, review]):
        path = sync.write_backup(plan, tmp_path)
    payload = json.loads(path.read_text())
    partition = payload["partitions_before"]["DRINK#drink-1"]
    assert {item["SK"] for item in partition} == {"METADATA", "TASTE_PROFILE", "REVIEW#1"}
    assert "password" not in path.read_text()


def test_rollback_never_removes_created_drink_with_new_review():
    backup = {
        "plan": {
            "operations": [{
                "action": "create_drink",
                "entity_id": "drink-1",
                "pk": "DRINK#drink-1",
                "after": {"PK": "DRINK#drink-1", "SK": "METADATA", "drink_id": "drink-1"},
            }]
        },
        "partitions_before": {"DRINK#drink-1": []},
    }
    current = [
        {"PK": "DRINK#drink-1", "SK": "METADATA", "drink_id": "drink-1"},
        {"PK": "DRINK#drink-1", "SK": "REVIEW#new", "review_id": "new"},
        {"PK": "DRINK#drink-1", "SK": "TASTE_PROFILE", "review_count": 1},
    ]
    with patch.object(rollback.db, "query_by_pk", return_value=current):
        operations, blocked = rollback.build_rollback_plan(backup)
    assert operations == []
    assert blocked[0]["reason"] == "new drink has Matcha Scout reviews"


def test_excluded_drinks_are_not_catalog_visible():
    from app.services.db import is_catalog_visible

    assert is_catalog_visible({"catalog_status": "active"})
    assert not is_catalog_visible({"catalog_status": "excluded"})


def test_retired_report_sync_fails_closed(capsys):
    from app.ingest.update_cafes_from_report import main

    assert main() == 2
    assert "retired" in capsys.readouterr().err
