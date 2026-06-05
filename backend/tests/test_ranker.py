"""
Tests for the recommendation ranking engine.
No DynamoDB, no API keys — pure unit tests of scoring and filtering logic.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from app.models.recommendation import RecommendationRequest
from app.services.ranker import rank_drinks, _score_drink, _dim_similarity

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_drink(drink_id, cafe_id, name, price, milk_options, strength, sweetness, creaminess, earthiness, bitterness):
    profile = {
        "drink_id": drink_id,
        "matcha_strength": strength,
        "sweetness": sweetness,
        "creaminess": creaminess,
        "earthiness": earthiness,
        "bitterness": bitterness,
        "review_count": 0,
        "last_updated": "2026-01-01T00:00:00",
    }
    return {
        "drink_id": drink_id,
        "cafe_id": cafe_id,
        "name": name,
        "price": price,
        "milk_options": milk_options,
        "description": "Test drink",
        "is_iced": True,
        "is_hot": False,
        "created_at": "2026-01-01T00:00:00",
        "profile": profile,
    }

CAFES = {"cafe-001": {"name": "Test Cafe"}}

STRONG_EARTHY = make_drink("d-strong", "cafe-001", "Strong Earthy", 7.0, ["none"], 5, 1, 1, 5, 5)
SWEET_CREAMY  = make_drink("d-sweet",  "cafe-001", "Sweet Creamy",  7.5, ["oat"],  1, 5, 5, 1, 1)
NEUTRAL       = make_drink("d-mid",    "cafe-001", "Neutral",       6.0, ["whole"], 3, 3, 3, 3, 3)
EXPENSIVE     = make_drink("d-exp",    "cafe-001", "Pricey",        12.0, ["oat"], 5, 1, 1, 5, 4)
OAT_ONLY      = make_drink("d-oat",   "cafe-001", "Oat Latte",     6.5, ["oat"],  3, 3, 4, 2, 2)
ALMOND_ONLY   = make_drink("d-almond","cafe-001", "Almond Latte",  6.0, ["almond"], 3, 3, 4, 2, 2)


# ── Similarity math ───────────────────────────────────────────────────────────

def test_exact_match_similarity_is_1():
    assert _dim_similarity(3.0, 3) == 1.0

def test_max_distance_similarity_is_0():
    assert _dim_similarity(1.0, 5) == 0.0
    assert _dim_similarity(5.0, 1) == 0.0

def test_half_distance_similarity_is_half():
    assert abs(_dim_similarity(3.0, 1) - 0.5) < 0.001


# ── Scoring ───────────────────────────────────────────────────────────────────

def test_exact_preference_match_scores_high():
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=5)
    score = _score_drink(prefs, STRONG_EARTHY["profile"])
    assert score >= 0.99

def test_opposite_preference_scores_low():
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=5)
    score = _score_drink(prefs, SWEET_CREAMY["profile"])
    assert score < 0.20

def test_score_clamped_between_0_and_1():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    score = _score_drink(prefs, NEUTRAL["profile"])
    assert 0.0 <= score <= 1.0


# ── Ranking order ─────────────────────────────────────────────────────────────

def test_results_sorted_by_match_pct_descending():
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=5)
    drinks = [SWEET_CREAMY, NEUTRAL, STRONG_EARTHY]
    results = rank_drinks(prefs, drinks, CAFES)
    pcts = [r.match_pct for r in results]
    assert pcts == sorted(pcts, reverse=True)

def test_closest_match_is_first():
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=5)
    drinks = [SWEET_CREAMY, NEUTRAL, STRONG_EARTHY]
    results = rank_drinks(prefs, drinks, CAFES)
    assert results[0].drink_id == "d-strong"


# ── Filters ───────────────────────────────────────────────────────────────────

def test_price_max_excludes_expensive_drinks():
    prefs = RecommendationRequest(matcha_strength=5, sweetness=1, creaminess=1, earthiness=5, bitterness=4, price_max=8.0)
    drinks = [STRONG_EARTHY, EXPENSIVE]
    results = rank_drinks(prefs, drinks, CAFES)
    drink_ids = [r.drink_id for r in results]
    assert "d-exp" not in drink_ids

def test_price_max_includes_drinks_at_or_under_limit():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3, price_max=7.0)
    drinks = [STRONG_EARTHY, NEUTRAL]  # $7.00 and $6.00
    results = rank_drinks(prefs, drinks, CAFES)
    assert len(results) == 2

def test_milk_type_filter_is_case_insensitive():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=4, earthiness=2, bitterness=2, milk_type="OAT")
    drinks = [OAT_ONLY, ALMOND_ONLY, STRONG_EARTHY]
    results = rank_drinks(prefs, drinks, CAFES)
    drink_ids = [r.drink_id for r in results]
    assert "d-oat" in drink_ids
    assert "d-almond" not in drink_ids
    assert "d-strong" not in drink_ids

def test_milk_type_none_returns_all_drinks():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drinks = [OAT_ONLY, ALMOND_ONLY, STRONG_EARTHY]
    results = rank_drinks(prefs, drinks, CAFES)
    assert len(results) == 3

def test_no_matches_returns_empty_list():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3, price_max=4.0)
    drinks = [STRONG_EARTHY, SWEET_CREAMY, EXPENSIVE]
    results = rank_drinks(prefs, drinks, CAFES)
    assert results == []

def test_limit_caps_results():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3, limit=2)
    drinks = [STRONG_EARTHY, SWEET_CREAMY, NEUTRAL, OAT_ONLY, ALMOND_ONLY]
    results = rank_drinks(prefs, drinks, CAFES)
    assert len(results) <= 2


# ── Reasons ───────────────────────────────────────────────────────────────────

def test_reasons_mention_milk_when_matched():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=4, earthiness=2, bitterness=2, milk_type="oat")
    drinks = [OAT_ONLY]
    results = rank_drinks(prefs, drinks, CAFES)
    assert any("oat" in r.lower() for r in results[0].reasons)

def test_reasons_mention_budget_when_under_price():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3, price_max=10.0)
    drinks = [NEUTRAL]
    results = rank_drinks(prefs, drinks, CAFES)
    assert any("budget" in r.lower() or "$" in r for r in results[0].reasons)

def test_reasons_not_empty():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    drinks = [NEUTRAL]
    results = rank_drinks(prefs, drinks, CAFES)
    assert len(results[0].reasons) > 0


# ── Response shape ────────────────────────────────────────────────────────────

def test_result_includes_cafe_name():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    results = rank_drinks(prefs, [NEUTRAL], CAFES)
    assert results[0].cafe_name == "Test Cafe"

def test_result_includes_taste_profile():
    prefs = RecommendationRequest(matcha_strength=3, sweetness=3, creaminess=3, earthiness=3, bitterness=3)
    results = rank_drinks(prefs, [NEUTRAL], CAFES)
    tp = results[0].taste_profile
    assert tp.matcha_strength == 3.0
    assert tp.sweetness == 3.0
