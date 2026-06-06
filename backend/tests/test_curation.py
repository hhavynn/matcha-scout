"""
Tests for the manual drink curation script.

All tests are pure unit tests or use mocked db calls.
No DynamoDB, no Yelp, no Gemini.
"""
from __future__ import annotations

import json
import sys
import os
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from app.ingest.manual_drink_curation import (
    CurationError,
    CurationResult,
    normalize_entry,
    process_entry,
    validate_drink_entry,
)
from app.models.taste_profile import compute_confidence


# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_CAFE = {
    "PK": "CAFE#cafe-001",
    "SK": "METADATA",
    "cafe_id": "cafe-001",
    "name": "Verdant Cup",
    "location": "Portland, OR",
    "created_at": "2026-06-05T00:00:00",
}

VALID_ENTRY = {
    "cafe_id": "cafe-001",
    "cafe_name_hint": "Verdant Cup",
    "name": "Iced Matcha Latte",
    "description": "A great matcha latte.",
    "price": 7.50,
    "milk_options": ["Oat", "Whole"],
    "is_iced": True,
    "is_hot": False,
    "verification_source": "official_menu",
    "verification_url": "https://menus.local/verdant",
    "verification_notes": "Verified from official menu.",
}


# ── validate_drink_entry ──────────────────────────────────────────────────────

def test_valid_entry_passes_validation():
    validate_drink_entry(VALID_ENTRY, 1)  # should not raise


def test_missing_name_rejected():
    entry = {**VALID_ENTRY, "name": ""}
    with pytest.raises(CurationError, match="name"):
        validate_drink_entry(entry, 1)


def test_name_none_rejected():
    entry = {**VALID_ENTRY}
    del entry["name"]
    with pytest.raises(CurationError, match="name"):
        validate_drink_entry(entry, 1)


def test_name_too_long_rejected():
    entry = {**VALID_ENTRY, "name": "x" * 121}
    with pytest.raises(CurationError, match="120"):
        validate_drink_entry(entry, 1)


def test_invalid_price_string_rejected():
    entry = {**VALID_ENTRY, "price": "seven dollars"}
    with pytest.raises(CurationError, match="price"):
        validate_drink_entry(entry, 1)


def test_negative_price_rejected():
    entry = {**VALID_ENTRY, "price": -1.0}
    with pytest.raises(CurationError, match="positive"):
        validate_drink_entry(entry, 1)


def test_zero_price_rejected():
    entry = {**VALID_ENTRY, "price": 0.0}
    with pytest.raises(CurationError, match="positive"):
        validate_drink_entry(entry, 1)


def test_price_none_is_valid():
    entry = {**VALID_ENTRY, "price": None}
    validate_drink_entry(entry, 1)  # no price is fine


def test_description_none_is_valid():
    entry = {**VALID_ENTRY, "description": None}
    validate_drink_entry(entry, 1)


def test_empty_milk_options_is_valid():
    entry = {**VALID_ENTRY, "milk_options": []}
    validate_drink_entry(entry, 1)


def test_milk_options_not_list_rejected():
    entry = {**VALID_ENTRY, "milk_options": "oat"}
    with pytest.raises(CurationError, match="milk_options"):
        validate_drink_entry(entry, 1)


def test_null_temperature_flags_are_valid():
    entry = {**VALID_ENTRY, "is_iced": None, "is_hot": None}
    validate_drink_entry(entry, 1)


def test_is_iced_non_bool_rejected():
    entry = {**VALID_ENTRY, "is_iced": "yes"}
    with pytest.raises(CurationError, match="is_iced"):
        validate_drink_entry(entry, 1)


def test_missing_cafe_reference_rejected():
    entry = {"name": "Matcha Latte"}  # no cafe_id or external source
    with pytest.raises(CurationError, match="cafe"):
        validate_drink_entry(entry, 1)


def test_cafe_via_external_source_passes():
    entry = {
        "cafe_external_source": "yelp",
        "cafe_external_id": "abc123",
        "name": "Matcha Latte",
        "verification_source": "official_menu",
        "verification_url": "https://menus.local/verdant",
    }
    validate_drink_entry(entry, 1)  # should not raise


def test_missing_verification_source_rejected():
    entry = {**VALID_ENTRY}
    del entry["verification_source"]
    with pytest.raises(CurationError, match="verification_source"):
        validate_drink_entry(entry, 1)


def test_missing_verification_url_and_notes_rejected():
    entry = {**VALID_ENTRY, "verification_url": None, "verification_notes": None}
    with pytest.raises(CurationError, match="verification_url"):
        validate_drink_entry(entry, 1)


def test_placeholder_name_rejected():
    entry = {**VALID_ENTRY, "name": "TODO Matcha Latte"}
    with pytest.raises(CurationError, match="placeholder"):
        validate_drink_entry(entry, 1)


def test_placeholder_verification_rejected():
    entry = {**VALID_ENTRY, "verification_notes": "TODO verify later"}
    with pytest.raises(CurationError, match="verification_notes"):
        validate_drink_entry(entry, 1)


# ── normalize_entry ───────────────────────────────────────────────────────────

def test_milk_options_normalized_to_lowercase():
    entry = {**VALID_ENTRY, "milk_options": ["OAT", "Whole", "ALMOND"]}
    result = normalize_entry(entry)
    assert result["milk_options"] == ["oat", "whole", "almond"]


def test_name_stripped():
    entry = {**VALID_ENTRY, "name": "  Iced Latte  "}
    result = normalize_entry(entry)
    assert result["name"] == "Iced Latte"


def test_defaults_applied():
    entry = {
        "cafe_id": "cafe-001",
        "name": "Latte",
        "verification_source": "official_menu",
        "verification_url": "https://menus.local/verdant",
    }
    result = normalize_entry(entry)
    assert "is_iced" not in result
    assert "is_hot" not in result
    assert result["milk_options"] == []
    assert result["verification_status"] == "admin_curated"


def test_explicit_verification_status_preserved():
    entry = {**VALID_ENTRY, "verification_status": "admin_verified"}
    result = normalize_entry(entry)
    assert result["verification_status"] == "admin_verified"


def test_verification_metadata_normalized():
    entry = {
        **VALID_ENTRY,
        "verification_source": " official_menu ",
        "verification_url": " https://menus.local/verdant ",
        "verification_notes": " Seen on menu. ",
    }
    result = normalize_entry(entry)
    assert result["verification_source"] == "official_menu"
    assert result["verification_url"] == "https://menus.local/verdant"
    assert result["verification_notes"] == "Seen on menu."


def test_normalize_does_not_mutate_input():
    entry = {**VALID_ENTRY, "milk_options": ["OAT"]}
    original_milk = list(entry["milk_options"])
    normalize_entry(entry)
    assert entry["milk_options"] == original_milk


# ── process_entry (dry-run) ───────────────────────────────────────────────────

def test_dry_run_does_not_write(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        process_entry(
            VALID_ENTRY, 1,
            applying=False,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    mock_db.create_admin_curated_drink.assert_not_called()
    assert len(result.would_create) == 1
    assert len(result.created) == 0


def test_dry_run_records_would_create(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        process_entry(
            VALID_ENTRY, 1,
            applying=False,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    assert "Iced Matcha Latte" in result.would_create[0]


# ── process_entry (missing cafe) ─────────────────────────────────────────────

def test_missing_cafe_prevents_write(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = None
        process_entry(
            VALID_ENTRY, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    mock_db.create_admin_curated_drink.assert_not_called()
    assert len(result.missing_cafe) == 1


# ── process_entry (existing drink skip) ──────────────────────────────────────

EXISTING_DRINK = {
    "PK": "DRINK#drink-abc",
    "SK": "METADATA",
    "drink_id": "drink-abc",
    "cafe_id": "cafe-001",
    "name": "Iced Matcha Latte",
}


def test_existing_drink_skipped_with_no_overwrite(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = EXISTING_DRINK
        process_entry(
            VALID_ENTRY, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    mock_db.create_admin_curated_drink.assert_not_called()
    assert len(result.skipped_existing) == 1


def test_existing_drink_written_with_allow_overwrite(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = EXISTING_DRINK
        mock_db.create_admin_curated_drink.return_value = {}
        process_entry(
            VALID_ENTRY, 1,
            applying=True,
            allow_overwrite=True,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    mock_db.create_admin_curated_drink.assert_called_once()


# ── process_entry (successful write) ─────────────────────────────────────────

def test_created_drink_has_correct_source_and_status(capsys):
    result = CurationResult()
    created_items = []

    def capture_create(cafe_id, drink):
        created_items.append(drink)
        return drink

    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        mock_db.create_admin_curated_drink.side_effect = capture_create
        process_entry(
            VALID_ENTRY, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )

    assert len(created_items) == 1
    drink = created_items[0]
    assert drink["source"] == "admin_curated"
    assert drink["verification_status"] == "admin_curated"
    assert drink["drink_id"].startswith("drink-")
    assert drink["cafe_id"] == "cafe-001"
    assert len(result.created) == 1


def test_created_drink_preserves_verification_metadata(capsys):
    result = CurationResult()
    created_items = []
    entry = {
        **VALID_ENTRY,
        "verification_source": "official_menu",
        "verification_url": "https://menus.local/verdant",
        "verification_notes": "Verified from official menu.",
    }

    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        mock_db.create_admin_curated_drink.side_effect = lambda cid, d: created_items.append(d) or d
        process_entry(
            entry, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )

    drink = created_items[0]
    assert drink["verification_source"] == "official_menu"
    assert drink["verification_url"] == "https://menus.local/verdant"
    assert drink["verification_notes"] == "Verified from official menu."


def test_created_drink_milk_normalized(capsys):
    result = CurationResult()
    created_items = []

    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        mock_db.create_admin_curated_drink.side_effect = lambda cid, d: created_items.append(d) or d
        entry = {**VALID_ENTRY, "milk_options": ["OAT", "WHOLE"]}
        process_entry(
            entry, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )

    assert created_items[0]["milk_options"] == ["oat", "whole"]


def test_created_drink_omits_unknown_temperature_fields(capsys):
    result = CurationResult()
    created_items = []
    entry = {**VALID_ENTRY, "milk_options": [], "is_iced": None, "is_hot": None}

    with patch("app.ingest.manual_drink_curation.db") as mock_db:
        mock_db.get_item.return_value = SAMPLE_CAFE
        mock_db.find_existing_drink_for_cafe.return_value = None
        mock_db.create_admin_curated_drink.side_effect = lambda cid, d: created_items.append(d) or d
        process_entry(
            entry, 1,
            applying=True,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )

    assert created_items[0]["milk_options"] == []
    assert "is_iced" not in created_items[0]
    assert "is_hot" not in created_items[0]


# ── db.create_admin_curated_drink initializes neutral taste profile ───────────

def test_create_admin_curated_drink_initializes_neutral_profile():
    """The DB helper must put two items: drink METADATA and TASTE_PROFILE."""
    put_calls = []

    from app.services.db import create_admin_curated_drink

    with patch("app.services.db.put_item", side_effect=lambda item: put_calls.append(item)):
        drink = {
            "drink_id": "drink-test-123",
            "cafe_id": "cafe-001",
            "name": "Test Matcha",
            "description": "",
            "price": Decimal("7.0"),
            "milk_options": ["oat"],
            "is_iced": True,
            "is_hot": False,
            "source": "admin_curated",
            "verification_status": "admin_curated",
            "created_at": "2026-06-05T00:00:00Z",
        }
        create_admin_curated_drink("cafe-001", drink)

    assert len(put_calls) == 2
    sks = {item["SK"] for item in put_calls}
    assert "METADATA" in sks
    assert "TASTE_PROFILE" in sks

    profile = next(i for i in put_calls if i["SK"] == "TASTE_PROFILE")
    assert profile["review_count"] == 0
    assert float(profile["matcha_strength"]) == 3.0
    assert float(profile["sweetness"]) == 3.0


def test_neutral_taste_profile_is_unrated():
    """review_count 0 → compute_confidence returns unrated."""
    label, score = compute_confidence(0)
    assert label == "unrated"
    assert score == 0.1


# ── invalid record handling ───────────────────────────────────────────────────

def test_invalid_entry_recorded_in_result(capsys):
    result = CurationResult()
    with patch("app.ingest.manual_drink_curation.db"):
        process_entry(
            {"cafe_id": "cafe-001", "name": ""},  # invalid: empty name
            1,
            applying=False,
            allow_overwrite=False,
            now="2026-06-05T00:00:00Z",
            result=result,
        )
    assert len(result.invalid_records) == 1


def test_non_dict_entry_handled_gracefully():
    """The main loop should handle non-dict entries without crashing."""
    from app.ingest.manual_drink_curation import run
    import tempfile

    payload = {
        "version": 1,
        "drinks": ["not-a-dict", None, 42],
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(payload, f)
        tmp_path = f.name

    class FakeArgs:
        file = tmp_path
        apply = False
        local = False
        allow_overwrite = False
        dry_run = True

    code = run(FakeArgs())
    assert code != 0  # non-zero because of invalid records


def test_apply_requires_target_flag(tmp_path):
    from app.ingest.manual_drink_curation import run

    payload = {"version": 1, "drinks": []}
    path = tmp_path / "drinks.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    class FakeArgs:
        file = str(path)
        apply = True
        local = False
        production = False
        confirm_production = False
        allow_overwrite = False
        dry_run = False

    assert run(FakeArgs()) == 2


def test_production_apply_requires_confirm_flag(tmp_path, monkeypatch):
    from app.ingest.manual_drink_curation import run

    payload = {"version": 1, "drinks": []}
    path = tmp_path / "drinks.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    class FakeArgs:
        file = str(path)
        apply = True
        local = False
        production = True
        confirm_production = False
        allow_overwrite = False
        dry_run = False

    monkeypatch.setattr("app.ingest.manual_drink_curation.settings.dynamodb_endpoint_url", None)
    assert run(FakeArgs()) == 2
