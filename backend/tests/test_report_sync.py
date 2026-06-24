from decimal import Decimal
from unittest.mock import patch

from app.ingest.sync_deep_research import (
    deterministic_drink_id,
    match_drink,
    normalize_name,
    resolve_cafe,
    values_equal,
)


def test_normalize_name_handles_apostrophes_accents_and_ampersands():
    assert normalize_name("Chance’s Café & Tea") == "chance s cafe and tea"


def test_match_cafe_accepts_report_alias():
    cafe = {"name": "The Barista Botanist", "cafe_id": "cafe-1"}
    entry = {"name": "Barista Botanist", "aliases": ["The Barista Botanist"]}
    assert resolve_cafe(entry, [cafe]) == (cafe, "exact_name")


def test_match_cafe_rejects_ambiguous_fuzzy_match():
    cafes = [
        {"name": "Communal North Park", "cafe_id": "cafe-1"},
        {"name": "Communal Oceanside", "cafe_id": "cafe-2"},
    ]
    assert resolve_cafe({"name": "Communal"}, cafes) == (None, "missing")


def test_match_drink_accepts_existing_alias():
    drink = {
        "name": "Premium Ceremonial Grade Matcha Latte",
        "price": Decimal("7"),
    }
    entry = {"name": "Labora 1", "aliases": ["Premium Ceremonial Grade Matcha Latte"]}
    assert match_drink(entry, [drink]) == drink


def test_deterministic_drink_id_is_stable_and_cafe_specific():
    first = deterministic_drink_id("cafe-1", "Strawberry Matcha")
    assert first == deterministic_drink_id("cafe-1", "Strawberry Matcha")
    assert first != deterministic_drink_id("cafe-2", "Strawberry Matcha")


def test_deep_research_match_rejects_address_conflict():
    entry = {
        "name": "Communal",
        "cafe_id": "cafe-1",
        "address": "2335 University Ave, San Diego, CA 92104",
    }
    cafes = [{
        "name": "Communal",
        "cafe_id": "cafe-1",
        "address": "2221 Fern St, San Diego, CA 92104",
    }]
    cafe, strategy = resolve_cafe(entry, cafes)
    assert cafe is None
    assert strategy == "address_conflict"


def test_values_equal_treats_decimal_and_float_as_same():
    assert values_equal(Decimal("7.50"), 7.5)


def test_recommendation_data_excludes_unrated_neutral_profiles():
    from app.services import db

    drinks = [
        {"drink_id": "unrated", "name": "Unrated Matcha"},
        {"drink_id": "reviewed", "name": "Reviewed Matcha"},
    ]
    profiles = [
        {"drink_id": "unrated", "review_count": 0},
        {"drink_id": "reviewed", "review_count": 1},
    ]
    with (
        patch("app.services.db.scan_by_entity_type", return_value=drinks),
        patch("app.services.db.scan_by_sk", return_value=profiles),
    ):
        result = db.get_all_drinks_with_profiles()

    assert [item["drink_id"] for item in result] == ["reviewed"]
