"""
Tests for region normalization, OC deduplication, and API filtering.
No real Yelp calls; all network access is mocked.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from fastapi.testclient import TestClient

from app.services.regions import normalize_region, OC_DEFAULT_LOCATIONS


# ── Region normalization ───────────────────────────────────────────────────────

def test_san_diego_normalizes():
    key, label = normalize_region("san-diego")
    assert key == "san-diego"
    assert label == "San Diego"


def test_orange_county_normalizes():
    key, label = normalize_region("orange-county")
    assert key == "orange-county"
    assert label == "Orange County"


def test_normalize_case_insensitive():
    key, label = normalize_region("ORANGE-COUNTY")
    assert key == "orange-county"
    assert label == "Orange County"


def test_normalize_unknown_region():
    key, label = normalize_region("tokyo")
    assert key == "unknown"
    assert label == "Unknown"


def test_oc_default_locations_are_all_california():
    for loc in OC_DEFAULT_LOCATIONS:
        assert loc.endswith(", CA"), f"Expected CA location, got: {loc}"


def test_oc_default_locations_count():
    assert len(OC_DEFAULT_LOCATIONS) >= 5, "Should have at least 5 OC cities"


# ── OC multi-city deduplication ───────────────────────────────────────────────

def _make_biz(yelp_id: str, name: str, city: str = "Irvine") -> dict:
    return {
        "id": yelp_id,
        "name": name,
        "rating": 4.0,
        "review_count": 100,
        "url": f"https://yelp.com/biz/{yelp_id}",
        "location": {
            "display_address": [f"123 Main St, {city}, CA 92620"],
            "city": city,
            "state": "CA",
        },
        "coordinates": {"latitude": 33.6, "longitude": -117.8},
        "categories": [{"title": "Cafes", "alias": "cafes"}],
    }


def test_dedup_removes_duplicates_across_cities():
    from app.ingest.yelp_region_ingestion import fetch_unique_businesses

    city_a_results = [_make_biz("biz-1", "Matcha A"), _make_biz("biz-2", "Matcha B")]
    city_b_results = [_make_biz("biz-2", "Matcha B"), _make_biz("biz-3", "Matcha C")]

    call_count = [0]
    def fake_search(term, location, limit, offset=0):
        result = [city_a_results, city_b_results][call_count[0]]
        call_count[0] += 1
        return result

    with patch("app.ingest.yelp_region_ingestion.search_businesses", side_effect=fake_search):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            results = fetch_unique_businesses("matcha", ["Irvine, CA", "Anaheim, CA"], 10, 0, 0.1)

    ids = [b["id"] for b in results]
    assert ids == ["biz-1", "biz-2", "biz-3"]
    assert len(ids) == len(set(ids)), "No duplicates expected"


def test_dedup_respects_limit():
    from app.ingest.yelp_region_ingestion import fetch_unique_businesses

    many_results = [_make_biz(f"biz-{i}", f"Cafe {i}") for i in range(20)]

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=many_results):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            results = fetch_unique_businesses("matcha", ["Irvine, CA"], 5, 0, 0.1)

    assert len(results) == 5


def test_oc_dry_run_does_not_write():
    """Running the ingestion script with --dry-run must never call db write methods."""
    from app.ingest.yelp_region_ingestion import run

    fake_biz = _make_biz("biz-oc-1", "OC Matcha")

    class FakeArgs:
        region = "orange-county"
        location = "Irvine, CA"
        term = "matcha"
        limit = 5
        offset = 0
        include_reviews = False
        dry_run = True
        apply = False
        local = False
        no_overwrite = False
        request_delay = 0.0

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
            with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                code = run(FakeArgs())

    mock_db.upsert_cafe_from_external_source.assert_not_called()
    assert code == 0


def test_ingestion_tags_region_key():
    """Ingested businesses must carry region_key and region_label."""
    from app.ingest.yelp_region_ingestion import run

    fake_biz = _make_biz("biz-sd-1", "SD Matcha Spot")
    captured = []

    class FakeArgs:
        region = "san-diego"
        location = "San Diego, CA"
        term = "matcha"
        limit = 5
        offset = 0
        include_reviews = False
        dry_run = False
        apply = True
        local = True
        no_overwrite = False
        request_delay = 0.0

    def fake_upsert(cafe, no_overwrite=False):
        captured.append(cafe)
        return cafe

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
            with patch("app.ingest.yelp_region_ingestion.settings") as mock_settings:
                mock_settings.dynamodb_endpoint_url = "http://localhost:8001"
                mock_settings.yelp_default_term = "matcha"
                mock_db.upsert_cafe_from_external_source.side_effect = fake_upsert
                with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                    run(FakeArgs())

    assert len(captured) == 1
    assert captured[0]["region_key"] == "san-diego"
    assert captured[0]["region_label"] == "San Diego"


def test_oc_ingestion_tags_orange_county():
    """Orange County ingestion should tag region_key='orange-county'."""
    from app.ingest.yelp_region_ingestion import run

    fake_biz = _make_biz("biz-oc-tag", "OC Matcha Spot", city="Irvine")
    captured = []

    class FakeArgs:
        region = "orange-county"
        location = "Irvine, CA"
        term = "matcha"
        limit = 5
        offset = 0
        include_reviews = False
        dry_run = False
        apply = True
        local = True
        no_overwrite = False
        request_delay = 0.0

    def fake_upsert(cafe, no_overwrite=False):
        captured.append(cafe)
        return cafe

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
            with patch("app.ingest.yelp_region_ingestion.settings") as mock_settings:
                mock_settings.dynamodb_endpoint_url = "http://localhost:8001"
                mock_settings.yelp_default_term = "matcha"
                mock_db.upsert_cafe_from_external_source.side_effect = fake_upsert
                with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                    run(FakeArgs())

    assert captured[0]["region_key"] == "orange-county"
    assert captured[0]["region_label"] == "Orange County"


# ── API region filtering ───────────────────────────────────────────────────────

SD_CAFE = {
    "PK": "CAFE#yelp-sd-1", "SK": "METADATA",
    "cafe_id": "yelp-sd-1", "name": "SD Matcha", "location": "San Diego, CA",
    "created_at": "2026-06-05T00:00:00", "source": "yelp",
    "region_key": "san-diego", "region_label": "San Diego",
}

OC_CAFE = {
    "PK": "CAFE#yelp-oc-1", "SK": "METADATA",
    "cafe_id": "yelp-oc-1", "name": "OC Matcha", "location": "Irvine, CA",
    "created_at": "2026-06-05T00:00:00", "source": "yelp",
    "region_key": "orange-county", "region_label": "Orange County",
}

NO_REGION_CAFE = {
    "PK": "CAFE#cafe-001", "SK": "METADATA",
    "cafe_id": "cafe-001", "name": "Seed Cafe", "location": "Portland, OR",
    "created_at": "2026-06-05T00:00:00",
}


def _make_test_client():
    from app.main import app
    return TestClient(app)


def test_get_cafes_no_filter_returns_all():
    client = _make_test_client()
    with patch("app.routers.cafes.db.scan_by_entity_type", return_value=[SD_CAFE, OC_CAFE, NO_REGION_CAFE]):
        resp = client.get("/cafes")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_cafes_san_diego_filter():
    client = _make_test_client()
    with patch("app.routers.cafes.db.scan_by_entity_type", return_value=[SD_CAFE, OC_CAFE, NO_REGION_CAFE]):
        resp = client.get("/cafes?region_key=san-diego")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "yelp-sd-1"


def test_get_cafes_orange_county_filter():
    client = _make_test_client()
    with patch("app.routers.cafes.db.scan_by_entity_type", return_value=[SD_CAFE, OC_CAFE, NO_REGION_CAFE]):
        resp = client.get("/cafes?region_key=orange-county")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "yelp-oc-1"


def test_get_cafes_unknown_region_returns_empty():
    client = _make_test_client()
    with patch("app.routers.cafes.db.scan_by_entity_type", return_value=[SD_CAFE, OC_CAFE]):
        resp = client.get("/cafes?region_key=seattle")
    assert resp.status_code == 200
    assert resp.json() == []


def test_recommendations_region_filter():
    """Recommendations with region_key should only include drinks from that region's cafes."""
    client = _make_test_client()
    sd_drink = {
        "drink_id": "drink-sd", "cafe_id": "yelp-sd-1", "name": "SD Latte",
        "price": "7.0", "milk_options": ["oat"], "description": "", "is_iced": True, "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "profile": {
            "matcha_strength": "3.0", "sweetness": "3.0", "creaminess": "3.0",
            "earthiness": "3.0", "bitterness": "3.0", "review_count": 0,
            "last_updated": "2026-06-05T00:00:00",
        },
    }
    oc_drink = {
        "drink_id": "drink-oc", "cafe_id": "yelp-oc-1", "name": "OC Latte",
        "price": "7.0", "milk_options": ["oat"], "description": "", "is_iced": True, "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "profile": {
            "matcha_strength": "3.0", "sweetness": "3.0", "creaminess": "3.0",
            "earthiness": "3.0", "bitterness": "3.0", "review_count": 0,
            "last_updated": "2026-06-05T00:00:00",
        },
    }
    cafes_map = {
        "yelp-sd-1": SD_CAFE,
        "yelp-oc-1": OC_CAFE,
    }

    with patch("app.routers.recommendations.db.get_all_drinks_with_profiles", return_value=[sd_drink, oc_drink]):
        with patch("app.routers.recommendations.db.get_all_cafes_by_id", return_value=cafes_map):
            resp = client.get(
                "/recommendations?matcha_strength=3&sweetness=3&creaminess=3"
                "&earthiness=3&bitterness=3&region_key=san-diego"
            )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["drink_id"] == "drink-sd"


def test_recommendations_no_region_returns_all():
    """Without region_key, recommendations include drinks from all regions."""
    client = _make_test_client()
    sd_drink = {
        "drink_id": "drink-sd2", "cafe_id": "yelp-sd-1", "name": "SD Latte 2",
        "price": "7.0", "milk_options": [], "description": "", "is_iced": True, "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "profile": {
            "matcha_strength": "3.0", "sweetness": "3.0", "creaminess": "3.0",
            "earthiness": "3.0", "bitterness": "3.0", "review_count": 0,
            "last_updated": "2026-06-05T00:00:00",
        },
    }
    oc_drink = {
        "drink_id": "drink-oc2", "cafe_id": "yelp-oc-1", "name": "OC Latte 2",
        "price": "7.0", "milk_options": [], "description": "", "is_iced": True, "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "profile": {
            "matcha_strength": "3.0", "sweetness": "3.0", "creaminess": "3.0",
            "earthiness": "3.0", "bitterness": "3.0", "review_count": 0,
            "last_updated": "2026-06-05T00:00:00",
        },
    }
    cafes_map = {"yelp-sd-1": SD_CAFE, "yelp-oc-1": OC_CAFE}

    with patch("app.routers.recommendations.db.get_all_drinks_with_profiles", return_value=[sd_drink, oc_drink]):
        with patch("app.routers.recommendations.db.get_all_cafes_by_id", return_value=cafes_map):
            resp = client.get(
                "/recommendations?matcha_strength=3&sweetness=3&creaminess=3&earthiness=3&bitterness=3"
            )
    assert resp.status_code == 200
    assert len(resp.json()) == 2
