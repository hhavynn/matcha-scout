"""
Tests for Phase 18 high-coverage Yelp ingestion safeguards.

All Yelp network calls are mocked. No real API calls made.
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

from app.ingest.yelp_region_ingestion import (
    CallCounter,
    _validate_write_mode,
    sweep_businesses,
)
from app.services.regions import (
    TERM_SETS,
    get_discovery_locations,
    get_term_set,
    SD_DISCOVERY_LOCATIONS,
    OC_DISCOVERY_LOCATIONS,
)


# ── CallCounter ───────────────────────────────────────────────────────────────

def test_call_counter_starts_at_zero():
    c = CallCounter(max_calls=100)
    assert c.used == 0
    assert c.can_make_call()


def test_call_counter_stops_at_max():
    c = CallCounter(max_calls=2)
    c.record_search()
    c.record_search()
    assert not c.can_make_call()
    assert c.used == 2


def test_call_counter_tracks_types():
    c = CallCounter(max_calls=100)
    c.record_search()
    c.record_search()
    c.record_review()
    assert c.search_calls == 2
    assert c.review_calls == 1
    assert c.used == 3


def test_call_counter_remaining():
    c = CallCounter(max_calls=10)
    c.record_search()
    assert c.remaining() == 9


# ── Write mode validation ─────────────────────────────────────────────────────

class _Args:
    """Minimal args stub."""
    def __init__(self, **kwargs):
        self.apply = False
        self.local = False
        self.production = False
        self.confirm_production = False
        self.__dict__.update(kwargs)


def test_no_apply_always_passes():
    args = _Args(apply=False)
    is_prod, err = _validate_write_mode(args)
    assert err == ""
    assert is_prod is False


def test_apply_requires_local_or_production():
    args = _Args(apply=True, local=False, production=False, confirm_production=False)
    with patch("app.ingest.yelp_region_ingestion.settings") as s:
        s.dynamodb_endpoint_url = None
        _, err = _validate_write_mode(args)
    assert err != ""
    assert "local" in err.lower() or "production" in err.lower()


def test_apply_production_requires_confirm():
    args = _Args(apply=True, production=True, confirm_production=False)
    is_prod, err = _validate_write_mode(args)
    assert is_prod is True
    assert "confirm-production" in err


def test_apply_production_with_confirm_succeeds():
    args = _Args(apply=True, production=True, confirm_production=True)
    is_prod, err = _validate_write_mode(args)
    assert is_prod is True
    assert err == ""


def test_apply_local_requires_endpoint():
    args = _Args(apply=True, local=True, production=False, confirm_production=False)
    with patch("app.ingest.yelp_region_ingestion.settings") as s:
        s.dynamodb_endpoint_url = None
        _, err = _validate_write_mode(args)
    assert "DYNAMODB_ENDPOINT_URL" in err


def test_apply_local_with_endpoint_succeeds():
    args = _Args(apply=True, local=True, production=False, confirm_production=False)
    with patch("app.ingest.yelp_region_ingestion.settings") as s:
        s.dynamodb_endpoint_url = "http://localhost:8001"
        is_prod, err = _validate_write_mode(args)
    assert is_prod is False
    assert err == ""


def test_local_and_production_are_mutually_exclusive():
    args = _Args(apply=True, local=True, production=True, confirm_production=True)
    with patch("app.ingest.yelp_region_ingestion.settings") as s:
        s.dynamodb_endpoint_url = "http://localhost:8001"
        _, err = _validate_write_mode(args)
    assert "mutually exclusive" in err


# ── High-coverage location lists ──────────────────────────────────────────────

def test_sd_discovery_locations_covers_all_required_cities():
    cities = " ".join(SD_DISCOVERY_LOCATIONS).lower()
    for expected in ["san diego", "la jolla", "chula vista", "carlsbad", "escondido"]:
        assert expected in cities, f"Expected city {expected!r} missing from SD locations"


def test_oc_discovery_locations_covers_all_required_cities():
    cities = " ".join(OC_DISCOVERY_LOCATIONS).lower()
    for expected in ["irvine", "costa mesa", "anaheim", "fullerton", "santa ana", "mission viejo"]:
        assert expected in cities, f"Expected city {expected!r} missing from OC locations"


def test_sd_discovery_has_at_least_10_locations():
    assert len(SD_DISCOVERY_LOCATIONS) >= 10


def test_oc_discovery_has_at_least_15_locations():
    assert len(OC_DISCOVERY_LOCATIONS) >= 15


def test_get_discovery_locations_high_coverage_sd():
    locs = get_discovery_locations("san-diego", high_coverage=True)
    assert len(locs) >= 10
    assert any("La Jolla" in l for l in locs)


def test_get_discovery_locations_high_coverage_oc():
    locs = get_discovery_locations("orange-county", high_coverage=True)
    assert len(locs) >= 15
    assert any("Mission Viejo" in l for l in locs)


# ── Term sets ─────────────────────────────────────────────────────────────────

def test_matcha_term_set_exists():
    terms = get_term_set("matcha")
    assert "matcha" in terms


def test_matcha_discovery_term_set_has_multiple_terms():
    terms = get_term_set("matcha-discovery")
    assert len(terms) >= 4
    assert "matcha" in terms


def test_unknown_term_set_raises():
    with pytest.raises(ValueError, match="Unknown term set"):
        get_term_set("nonexistent-set")


# ── sweep_businesses deduplication ───────────────────────────────────────────

def _make_biz(yelp_id: str, name: str = "Cafe") -> dict:
    return {
        "id": yelp_id, "name": name, "rating": 4.0, "review_count": 100,
        "url": f"https://yelp.com/biz/{yelp_id}",
        "location": {"display_address": ["123 Main St, Irvine, CA"], "city": "Irvine", "state": "CA"},
        "coordinates": {"latitude": 33.6, "longitude": -117.8},
        "categories": [{"title": "Cafes", "alias": "cafes"}],
    }


def test_sweep_deduplicates_across_terms():
    biz_a = _make_biz("biz-1", "Matcha A")
    biz_b = _make_biz("biz-2", "Matcha B")

    call_idx = [0]
    responses = [[biz_a, biz_b], [biz_b]]  # term 2 repeats biz_b

    def fake_search(term, location, limit, offset=0):
        resp = responses[min(call_idx[0], len(responses) - 1)]
        call_idx[0] += 1
        return resp

    counter = CallCounter(max_calls=50)
    with patch("app.ingest.yelp_region_ingestion.search_businesses", side_effect=fake_search):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            unique, dupes = sweep_businesses(
                ["matcha", "japanese cafe"], ["Irvine, CA"], 10, counter, 0.0
            )
    ids = [b["id"] for b in unique]
    assert ids == ["biz-1", "biz-2"]
    assert dupes == 1  # biz_b repeated


def test_sweep_respects_max_api_calls():
    """Sweep stops when CallCounter hits max."""
    always_return = [_make_biz(f"biz-{i}") for i in range(50)]

    counter = CallCounter(max_calls=2)  # Only allow 2 search calls
    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=always_return):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            unique, _ = sweep_businesses(
                ["matcha", "tea", "boba"], ["Irvine, CA", "Anaheim, CA"],
                1000, counter, 0.0
            )
    assert counter.used == 2
    assert len(unique) <= 100  # 2 calls × up to 50 each


def test_sweep_respects_target():
    always_return = [_make_biz(f"biz-{i}") for i in range(50)]

    counter = CallCounter(max_calls=500)
    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=always_return):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            unique, _ = sweep_businesses(
                ["matcha"], ["Irvine, CA"], 15, counter, 0.0
            )
    assert len(unique) == 15


def test_sweep_paginates_when_full_page_returned():
    """If 50 results returned, should try next page."""
    page0 = [_make_biz(f"biz-p0-{i}") for i in range(50)]
    page1 = [_make_biz(f"biz-p1-{i}") for i in range(10)]  # Partial page — stop here

    offsets_seen = []

    def fake_search(term, location, limit, offset=0):
        offsets_seen.append(offset)
        return page0 if offset == 0 else page1

    counter = CallCounter(max_calls=50)
    with patch("app.ingest.yelp_region_ingestion.search_businesses", side_effect=fake_search):
        with patch("app.ingest.yelp_region_ingestion.time.sleep"):
            unique, _ = sweep_businesses(["matcha"], ["Irvine, CA"], 100, counter, 0.0)

    assert 0 in offsets_seen
    assert 50 in offsets_seen
    assert len(unique) == 60  # 50 + 10


# ── No-reviews enforcement ────────────────────────────────────────────────────

def test_dry_run_no_writes():
    from app.ingest.yelp_region_ingestion import run

    class FakeArgs:
        region = "san-diego"
        location = "San Diego, CA"
        term = "matcha"
        term_set = "matcha"
        target = 3
        max_api_calls = 20
        high_coverage = False
        no_reviews = True
        include_reviews = False
        request_delay = 0.0
        no_overwrite = False
        dry_run = True
        apply = False
        local = False
        production = False
        confirm_production = False

    fake_biz = _make_biz("biz-sd-test", "SD Dry Run Cafe")

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
            with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                code = run(FakeArgs())

    mock_db.upsert_cafe_from_external_source.assert_not_called()
    mock_db.get_business_reviews.assert_not_called() if hasattr(mock_db, 'get_business_reviews') else None
    assert code == 0


def test_no_reviews_mode_does_not_call_reviews_endpoint():
    from app.ingest.yelp_region_ingestion import run

    class FakeArgs:
        region = "san-diego"
        location = "San Diego, CA"
        term = "matcha"
        term_set = "matcha"
        target = 3
        max_api_calls = 20
        high_coverage = False
        no_reviews = True
        include_reviews = False
        request_delay = 0.0
        no_overwrite = False
        dry_run = False
        apply = True
        local = True
        production = False
        confirm_production = False

    fake_biz = _make_biz("biz-noreview", "No Review Cafe")

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.get_business_reviews") as mock_reviews:
            with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
                with patch("app.ingest.yelp_region_ingestion.settings") as mock_settings:
                    mock_settings.dynamodb_endpoint_url = "http://localhost:8001"
                    mock_db.get_item.return_value = None
                    mock_db.upsert_cafe_from_external_source.return_value = {"cafe_id": "yelp-biz-noreview"}
                    with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                        run(FakeArgs())
    mock_reviews.assert_not_called()


def test_production_write_does_not_require_local_endpoint():
    """Production apply must work without DYNAMODB_ENDPOINT_URL."""
    from app.ingest.yelp_region_ingestion import run

    class FakeArgs:
        region = "san-diego"
        location = "San Diego, CA"
        term = "matcha"
        term_set = "matcha"
        target = 2
        max_api_calls = 10
        high_coverage = False
        no_reviews = True
        include_reviews = False
        request_delay = 0.0
        no_overwrite = False
        dry_run = False
        apply = True
        local = False
        production = True
        confirm_production = True

    fake_biz = _make_biz("biz-prod-test", "Prod Test Cafe")

    with patch("app.ingest.yelp_region_ingestion.search_businesses", return_value=[fake_biz]):
        with patch("app.ingest.yelp_region_ingestion.db") as mock_db:
            with patch("app.ingest.yelp_region_ingestion.settings") as mock_settings:
                # Production: no local endpoint
                mock_settings.dynamodb_endpoint_url = None
                mock_db.get_item.return_value = None
                mock_db.upsert_cafe_from_external_source.return_value = {"cafe_id": "yelp-biz-prod-test"}
                with patch("app.ingest.yelp_region_ingestion.time.sleep"):
                    code = run(FakeArgs())

    mock_db.upsert_cafe_from_external_source.assert_called_once()
    assert code == 0
