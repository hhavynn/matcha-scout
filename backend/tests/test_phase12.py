"""
Phase 12 tests: user-submitted drinks and confidence scoring.

All tests are pure unit tests — no DynamoDB, no Yelp, no Gemini.
Router tests use FastAPI TestClient with mocked db calls.
"""
import sys
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from fastapi.testclient import TestClient

from app.models.taste_profile import compute_confidence
from app.models.recommendation import RecommendationRequest, RecommendationResult
from app.services.ranker import rank_drinks, _score_drink


# ── Confidence computation ─────────────────────────────────────────────────────

def test_zero_reviews_is_unrated():
    label, score = compute_confidence(0)
    assert label == "unrated"
    assert score == 0.1


def test_one_review_is_low():
    label, score = compute_confidence(1)
    assert label == "low"
    assert score == 0.35


def test_two_reviews_is_medium():
    label, score = compute_confidence(2)
    assert label == "medium"
    assert score == 0.65


def test_four_reviews_is_medium():
    label, score = compute_confidence(4)
    assert label == "medium"
    assert score == 0.65


def test_five_reviews_is_high():
    label, score = compute_confidence(5)
    assert label == "high"
    assert score == 0.9


def test_many_reviews_is_high():
    label, score = compute_confidence(100)
    assert label == "high"
    assert score == 0.9


def test_confidence_score_order():
    _, unrated = compute_confidence(0)
    _, low = compute_confidence(1)
    _, medium = compute_confidence(3)
    _, high = compute_confidence(5)
    assert unrated < low < medium < high


# ── Ranker: confidence included in results ─────────────────────────────────────

def make_drink_with_profile(drink_id, review_count=0, strength=3, sweetness=3,
                              creaminess=3, earthiness=3, bitterness=3, price=7.0):
    profile = {
        "drink_id": drink_id,
        "matcha_strength": strength,
        "sweetness": sweetness,
        "creaminess": creaminess,
        "earthiness": earthiness,
        "bitterness": bitterness,
        "review_count": review_count,
        "last_updated": "2026-06-05T00:00:00",
    }
    return {
        "drink_id": drink_id,
        "cafe_id": "cafe-001",
        "name": f"Drink {drink_id}",
        "price": price,
        "milk_options": ["oat"],
        "description": "Test",
        "is_iced": True,
        "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "profile": profile,
    }


CAFES = {"cafe-001": {"name": "Test Cafe"}}


def test_recommendations_include_confidence_label():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drink = make_drink_with_profile("d-001", review_count=0)
    results = rank_drinks(prefs, [drink], CAFES)
    assert len(results) == 1
    assert results[0].confidence_label == "unrated"
    assert results[0].confidence_score == 0.1


def test_recommendations_include_confidence_score():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drink = make_drink_with_profile("d-002", review_count=5)
    results = rank_drinks(prefs, [drink], CAFES)
    assert results[0].confidence_label == "high"
    assert results[0].confidence_score == 0.9


def test_taste_profile_snapshot_includes_confidence():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drink = make_drink_with_profile("d-003", review_count=2)
    results = rank_drinks(prefs, [drink], CAFES)
    tp = results[0].taste_profile
    assert tp.confidence_label == "medium"
    assert tp.confidence_score == 0.65


def test_recommendations_sort_primary_by_match_pct():
    """match_pct must be the primary sort key — confidence is only a tiebreaker."""
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=5)
    # d-perfect matches prefs exactly but has no reviews
    d_perfect = make_drink_with_profile("d-perfect", review_count=0,
                                        strength=5, sweetness=1, creaminess=1,
                                        earthiness=5, bitterness=5)
    # d-high_conf is a neutral drink with many reviews (high confidence but poor match)
    d_high_conf = make_drink_with_profile("d-high-conf", review_count=10,
                                          strength=3, sweetness=3, creaminess=3,
                                          earthiness=3, bitterness=3)
    results = rank_drinks(prefs, [d_high_conf, d_perfect], CAFES)
    assert results[0].drink_id == "d-perfect", (
        "Perfect taste match should rank first regardless of confidence"
    )


def test_confidence_tiebreaker_among_equal_match():
    """When match_pct is identical, higher confidence should rank first."""
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    d_no_reviews = make_drink_with_profile("d-no-rev", review_count=0, price=7.0)
    d_many_reviews = make_drink_with_profile("d-many-rev", review_count=10, price=8.0)
    results = rank_drinks(prefs, [d_no_reviews, d_many_reviews], CAFES)
    assert results[0].drink_id == "d-many-rev", (
        "Higher confidence drink should win the tiebreaker"
    )


# ── Router tests: create drink under a cafe ────────────────────────────────────

SAMPLE_CAFE_ITEM = {
    "PK": "CAFE#cafe-001",
    "SK": "METADATA",
    "cafe_id": "cafe-001",
    "name": "Verdant Cup",
    "location": "Portland, OR",
    "created_at": "2026-06-05T00:00:00",
}

SAMPLE_DRINK_ITEM = {
    "PK": "DRINK#drink-abc",
    "SK": "METADATA",
    "GSI1PK": "CAFE#cafe-001",
    "GSI1SK": "DRINK#drink-abc",
    "drink_id": "drink-abc",
    "cafe_id": "cafe-001",
    "name": "Iced Oat Matcha Latte",
    "description": "User-submitted test",
    "price": Decimal("7.5"),
    "milk_options": ["oat"],
    "is_iced": True,
    "is_hot": False,
    "source": "user_submitted",
    "verification_status": "unverified",
    "submitted_at": "2026-06-05T00:00:00",
    "created_at": "2026-06-05T00:00:00",
}


def _make_test_client():
    from app.main import app
    return TestClient(app)


def test_create_drink_under_existing_cafe():
    client = _make_test_client()
    with (
        patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM),
        patch("app.routers.cafes.db.put_item", return_value=None),
    ):
        resp = client.post("/cafes/cafe-001/drinks", json={
            "name": "Iced Oat Matcha Latte",
            "description": "User-submitted test",
            "price": 7.5,
            "milk_options": ["Oat"],
            "is_iced": True,
            "is_hot": False,
        })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "Iced Oat Matcha Latte"
    assert data["cafe_id"] == "cafe-001"
    assert data["source"] == "user_submitted"
    assert data["verification_status"] == "unverified"
    assert data["id"].startswith("drink-")


def test_create_drink_milk_options_normalized_lowercase():
    client = _make_test_client()
    with (
        patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM),
        patch("app.routers.cafes.db.put_item", return_value=None),
    ):
        resp = client.post("/cafes/cafe-001/drinks", json={
            "name": "Latte",
            "milk_options": ["OAT", "Whole", "ALMOND"],
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["milk_options"] == ["oat", "whole", "almond"]


def test_create_drink_under_missing_cafe_returns_404():
    client = _make_test_client()
    with patch("app.routers.cafes.db.get_item", return_value=None):
        resp = client.post("/cafes/nonexistent/drinks", json={"name": "Test"})
    assert resp.status_code == 404


def test_create_drink_defaults_source_and_verification():
    client = _make_test_client()
    with (
        patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM),
        patch("app.routers.cafes.db.put_item", return_value=None),
    ):
        resp = client.post("/cafes/cafe-001/drinks", json={"name": "Simple Matcha"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["source"] == "user_submitted"
    assert data["verification_status"] == "unverified"


def test_create_drink_name_required():
    client = _make_test_client()
    with patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM):
        resp = client.post("/cafes/cafe-001/drinks", json={})
    assert resp.status_code == 422


def test_create_drink_price_must_be_positive():
    client = _make_test_client()
    with patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM):
        resp = client.post("/cafes/cafe-001/drinks", json={"name": "Test", "price": -1.0})
    assert resp.status_code == 422


def test_list_cafe_drinks_existing_cafe():
    client = _make_test_client()
    with (
        patch("app.routers.cafes.db.get_item", return_value=SAMPLE_CAFE_ITEM),
        patch("app.routers.cafes.db.query_gsi", return_value=[SAMPLE_DRINK_ITEM]),
    ):
        resp = client.get("/cafes/cafe-001/drinks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Iced Oat Matcha Latte"


def test_list_cafe_drinks_missing_cafe_returns_404():
    client = _make_test_client()
    with patch("app.routers.cafes.db.get_item", return_value=None):
        resp = client.get("/cafes/nonexistent/drinks")
    assert resp.status_code == 404


# ── Yelp excerpts do NOT influence taste profile confidence ────────────────────

def test_yelp_excerpt_does_not_affect_confidence():
    """
    Confidence comes only from Matcha Scout review_count.
    A drink with many Yelp excerpts but 0 MS reviews is still "unrated".
    """
    yelp_excerpt_count = 100
    review_count = 0
    label, score = compute_confidence(review_count)
    # Even with 100 Yelp excerpts, confidence is driven by review_count only
    assert label == "unrated"
    assert score == 0.1
    # Verify the function signature only accepts review_count (no yelp param)
    import inspect
    sig = inspect.signature(compute_confidence)
    assert list(sig.parameters.keys()) == ["review_count"]


def test_yelp_rating_does_not_affect_ranker_confidence():
    """
    A drink with a high Yelp rating (if stored as cafe metadata) should NOT
    change the taste profile confidence in recommendation results.
    """
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drink = make_drink_with_profile("d-yelp", review_count=0)
    # Simulate a cafe with a high Yelp rating
    cafes = {"cafe-001": {"name": "Top Yelp Cafe", "rating": 4.9, "review_count": 500}}
    results = rank_drinks(prefs, [drink], cafes)
    # Taste profile confidence is still "unrated" — Yelp data is irrelevant here
    assert results[0].confidence_label == "unrated"
    assert results[0].taste_profile.confidence_label == "unrated"
