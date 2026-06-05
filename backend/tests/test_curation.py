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


def test_milk_options_not_list_rejected():
    entry = {**VALID_ENTRY, "milk_options": "oat"}
    with pytest.raises(CurationError, match="milk_options"):
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
    }
    validate_drink_entry(entry, 1)  # should not raise


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
    entry = {"cafe_id": "cafe-001", "name": "Latte"}
    result = normalize_entry(entry)
    assert result["is_iced"] is True
    assert result["is_hot"] is False
    assert result["verification_status"] == "admin_curated"


def test_explicit_verification_status_preserved():
    entry = {**VALID_ENTRY, "verification_status": "admin_verified"}
    result = normalize_entry(entry)
    assert result["verification_status"] == "admin_verified"


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
