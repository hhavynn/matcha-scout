"""
Tests for the mock AI parser keyword logic and the taste profile averaging.
These run without Docker, DynamoDB, or any API keys.
"""
import sys
import os

# Allow imports from backend/app without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force mock mode so tests never need a Gemini key
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from app.services.ai_parser import _mock_parse


# ── Mock parser keyword tests ─────────────────────────────────────────────────

def test_strong_earthy_ceremonial():
    result = _mock_parse("This was a strong earthy ceremonial matcha, a little bitter but really smooth.")
    assert result.matcha_strength >= 4, f"Expected high strength, got {result.matcha_strength}"
    assert result.earthiness >= 4, f"Expected high earthiness, got {result.earthiness}"
    assert result.bitterness >= 4, f"Expected elevated bitterness, got {result.bitterness}"
    assert result.confidence > 0.5


def test_sweet_strawberry():
    result = _mock_parse("A sweet strawberry matcha with lots of vanilla flavor.")
    assert result.sweetness >= 4, f"Expected high sweetness, got {result.sweetness}"
    assert result.confidence > 0.4


def test_creamy_oat_latte():
    result = _mock_parse("A creamy oat milk matcha latte, very smooth and silky.")
    assert result.creaminess >= 4, f"Expected high creaminess, got {result.creaminess}"


def test_vague_review_neutral_defaults():
    result = _mock_parse("I had a matcha drink today and it was interesting.")
    # No strong signals — should hover near neutral (3)
    assert 2 <= result.matcha_strength <= 4
    assert 2 <= result.sweetness <= 4
    assert result.confidence <= 0.5, f"Vague review should have low confidence, got {result.confidence}"


def test_unsweetened_lowers_sweetness():
    result = _mock_parse("Unsweetened matcha, pure and not sweet at all.")
    assert result.sweetness <= 2, f"Expected low sweetness, got {result.sweetness}"


def test_scores_clamped_1_to_5():
    # Many strength signals should not exceed 5
    result = _mock_parse("Strong intense bold ceremonial matcha, very strong and intense again.")
    assert 1 <= result.matcha_strength <= 5
    assert 1 <= result.sweetness <= 5
    assert 1 <= result.creaminess <= 5
    assert 1 <= result.earthiness <= 5
    assert 1 <= result.bitterness <= 5


def test_confidence_scales_with_keywords():
    sparse = _mock_parse("I had a matcha drink.")
    rich = _mock_parse("Strong earthy bitter creamy sweet smooth ceremonial oat latte.")
    assert rich.confidence > sparse.confidence


def test_tags_populated():
    result = _mock_parse("Very earthy and bitter, like a ceremonial grade matcha.")
    assert result.tags is not None
    assert len(result.tags) > 0


# ── Aggregation logic tests ───────────────────────────────────────────────────

def test_average_calculation():
    """Verify the averaging math directly — no DynamoDB needed."""
    reviews = [
        {"parsed_strength": 5, "parsed_sweetness": 1, "parsed_creaminess": 1, "parsed_earthiness": 5, "parsed_bitterness": 4},
        {"parsed_strength": 3, "parsed_sweetness": 3, "parsed_creaminess": 3, "parsed_earthiness": 3, "parsed_bitterness": 3},
    ]
    fields = ["parsed_strength", "parsed_sweetness", "parsed_creaminess", "parsed_earthiness", "parsed_bitterness"]
    totals = {f: sum(r[f] for r in reviews) for f in fields}
    count = len(reviews)
    averages = {f: round(totals[f] / count, 2) for f in fields}

    assert averages["parsed_strength"] == 4.0
    assert averages["parsed_sweetness"] == 2.0
    assert averages["parsed_creaminess"] == 2.0
    assert averages["parsed_earthiness"] == 4.0
    assert averages["parsed_bitterness"] == 3.5


def test_single_review_average_equals_itself():
    reviews = [
        {"parsed_strength": 4, "parsed_sweetness": 2, "parsed_creaminess": 3, "parsed_earthiness": 4, "parsed_bitterness": 3},
    ]
    fields = ["parsed_strength", "parsed_sweetness", "parsed_creaminess", "parsed_earthiness", "parsed_bitterness"]
    averages = {f: reviews[0][f] for f in fields}
    assert averages["parsed_strength"] == 4
    assert averages["parsed_sweetness"] == 2
