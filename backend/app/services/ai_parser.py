"""
Parses free-text matcha reviews into structured taste profiles.

Two modes:
  USE_MOCK_AI=true  → deterministic keyword-based mock (no API calls)
  USE_MOCK_AI=false → Gemini Flash structured output via google-genai SDK
"""
import json
from fastapi import HTTPException
from app.core.config import settings
from app.models.review import ParsedTasteProfile

# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a matcha drink taste analyzer. Given a user's review of a matcha drink,
extract numeric taste ratings on a 1–5 scale where 1 is very low and 5 is very high.

Definitions:
- matcha_strength: How pronounced and intense the matcha flavor is (1=very mild, 5=very strong/dominant)
- sweetness: Overall sweetness of the drink (1=not sweet, 5=very sweet)
- creaminess: Texture and dairy/milk richness (1=watery/thin, 5=very thick and creamy)
- earthiness: Grassy, vegetal, umami depth of the matcha (1=none, 5=very earthy/grassy)
- bitterness: Bitter edge of the matcha (1=not bitter, 5=very bitter)
- confidence: Your confidence in these ratings given the information in the review (0.0–1.0)
- summary: One sentence describing the drink based on the review (optional, max 100 chars)
- tags: 2–4 short descriptive tags like ["earthy", "strong", "ceremonial"] (optional)

If the review is too vague to rate a dimension, default to 3 (neutral).
Lower confidence when the review gives little taste detail."""

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "matcha_strength": {"type": "integer", "minimum": 1, "maximum": 5},
        "sweetness":       {"type": "integer", "minimum": 1, "maximum": 5},
        "creaminess":      {"type": "integer", "minimum": 1, "maximum": 5},
        "earthiness":      {"type": "integer", "minimum": 1, "maximum": 5},
        "bitterness":      {"type": "integer", "minimum": 1, "maximum": 5},
        "confidence":      {"type": "number",  "minimum": 0.0, "maximum": 1.0},
        "summary":         {"type": "string"},
        "tags":            {"type": "array", "items": {"type": "string"}},
    },
    "required": ["matcha_strength", "sweetness", "creaminess", "earthiness", "bitterness", "confidence"],
}

# ── Mock parser ───────────────────────────────────────────────────────────────

_KEYWORD_SIGNALS: dict[str, dict[str, int]] = {
    # strength signals
    "strong":       {"matcha_strength": 2},
    "intense":      {"matcha_strength": 2},
    "bold":         {"matcha_strength": 1},
    "mild":         {"matcha_strength": -2},
    "weak":         {"matcha_strength": -2},
    "light":        {"matcha_strength": -1},
    "ceremonial":   {"matcha_strength": 2, "earthiness": 1},
    # sweetness signals
    "sweet":        {"sweetness": 2},
    "sugary":       {"sweetness": 2},
    "vanilla":      {"sweetness": 1},
    "strawberry":   {"sweetness": 2},
    "honey":        {"sweetness": 1},
    "unsweetened":  {"sweetness": -2},
    "not sweet":    {"sweetness": -2},
    # creaminess signals
    "creamy":       {"creaminess": 2},
    "smooth":       {"creaminess": 1},
    "silky":        {"creaminess": 1},
    "oat":          {"creaminess": 1},
    "milk":         {"creaminess": 1},
    "latte":        {"creaminess": 1},
    "watery":       {"creaminess": -2},
    "thin":         {"creaminess": -1},
    # earthiness signals
    "earthy":       {"earthiness": 2},
    "grassy":       {"earthiness": 2},
    "vegetal":      {"earthiness": 2},
    "umami":        {"earthiness": 1},
    "nutty":        {"earthiness": 1},
    # bitterness signals
    "bitter":       {"bitterness": 2},
    "astringent":   {"bitterness": 2},
    "sharp":        {"bitterness": 1},
    "mellow":       {"bitterness": -1},
}


def _mock_parse(raw_text: str) -> ParsedTasteProfile:
    text = raw_text.lower()
    scores = {
        "matcha_strength": 3,
        "sweetness": 3,
        "creaminess": 3,
        "earthiness": 3,
        "bitterness": 3,
    }
    matched_keywords = []

    for keyword, adjustments in _KEYWORD_SIGNALS.items():
        if keyword in text:
            matched_keywords.append(keyword)
            for dim, delta in adjustments.items():
                scores[dim] = max(1, min(5, scores[dim] + delta))

    confidence = min(0.9, 0.4 + len(matched_keywords) * 0.1)
    tags = matched_keywords[:4] if matched_keywords else ["matcha"]

    return ParsedTasteProfile(
        matcha_strength=scores["matcha_strength"],
        sweetness=scores["sweetness"],
        creaminess=scores["creaminess"],
        earthiness=scores["earthiness"],
        bitterness=scores["bitterness"],
        confidence=round(confidence, 2),
        summary=f"Mock parse based on {len(matched_keywords)} keyword(s) detected.",
        tags=tags,
    )


# ── Gemini parser ─────────────────────────────────────────────────────────────

def _gemini_parse(raw_text: str) -> ParsedTasteProfile:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "Gemini is not configured. Set GEMINI_API_KEY in your .env file, "
                "or set USE_MOCK_AI=true to use the local mock parser."
            ),
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="google-genai package is not installed. Rebuild the Docker image.",
        )

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{_SYSTEM_PROMPT}\n\nReview to analyze:\n{raw_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_RESPONSE_SCHEMA,
                temperature=0.2,
            ),
        )
        raw_json = response.text
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API call failed: {str(e)}",
        )

    try:
        data = json.loads(raw_json)
        return ParsedTasteProfile(**data)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini returned malformed output: {str(e)}. Raw: {raw_json[:200]}",
        )


# ── Public interface ──────────────────────────────────────────────────────────

def parse_matcha_review(raw_text: str) -> ParsedTasteProfile:
    if settings.use_mock_ai:
        return _mock_parse(raw_text)
    return _gemini_parse(raw_text)
