"""
Deterministic recommendation engine for Matcha Scout.

Scoring formula (per taste dimension):
  similarity = 1 - abs(drink_value - preference_value) / MAX_DISTANCE
  weighted_score = sum(similarity_i * weight_i) / sum(weight_i)
  match_pct = round(weighted_score * 100)

MAX_DISTANCE = 4 (the maximum gap on a 1–5 scale is 5 - 1 = 4)

Weights reflect how much each dimension typically matters to a matcha drinker:
  matcha_strength: 1.25  — core identity of the drink
  sweetness:       1.10  — strong personal preference split
  creaminess:      1.00  — baseline importance
  earthiness:      1.00  — baseline importance
  bitterness:      0.80  — matters less; people are more tolerant of mismatch
"""
from app.models.recommendation import RecommendationRequest, RecommendationResult, TasteProfileSnapshot
from app.models.taste_profile import compute_confidence

MAX_DISTANCE = 4.0

WEIGHTS: dict[str, float] = {
    "matcha_strength": 1.25,
    "sweetness":       1.10,
    "creaminess":      1.00,
    "earthiness":      1.00,
    "bitterness":      0.80,
}

DIMENSION_LABELS: dict[str, str] = {
    "matcha_strength": "matcha strength",
    "sweetness":       "sweetness",
    "creaminess":      "creaminess",
    "earthiness":      "earthiness",
    "bitterness":      "bitterness",
}

# How close a dimension value needs to be to generate a positive reason
CLOSE_THRESHOLD = 1.0
# How far before generating a "off but close overall" reason
FAR_THRESHOLD = 2.5


def _dim_similarity(drink_val: float, pref_val: float) -> float:
    return 1.0 - abs(drink_val - pref_val) / MAX_DISTANCE


def _score_drink(prefs: RecommendationRequest, profile: dict) -> float:
    """Return weighted similarity score in [0, 1]."""
    total_weight = sum(WEIGHTS.values())
    weighted_sum = 0.0
    for dim, weight in WEIGHTS.items():
        pref_val = getattr(prefs, dim)
        drink_val = float(profile[dim])
        weighted_sum += _dim_similarity(drink_val, pref_val) * weight
    return weighted_sum / total_weight


def _build_reasons(
    prefs: RecommendationRequest,
    profile: dict,
    drink: dict,
    match_pct: int,
) -> list[str]:
    # Filter-based reasons come first — they directly reflect user intent
    priority_reasons: list[str] = []

    if prefs.milk_type:
        milk_lower = prefs.milk_type.lower()
        options_lower = [m.lower() for m in drink.get("milk_options", [])]
        if milk_lower in options_lower:
            priority_reasons.append(f"Available with {prefs.milk_type} milk")

    price_value = drink.get("price")
    if prefs.price_max and price_value is not None and float(price_value) <= prefs.price_max:
        priority_reasons.append(f"Under your ${prefs.price_max:.2f} budget")

    # Taste dimension reasons
    taste_reasons: list[str] = []
    for dim, label in DIMENSION_LABELS.items():
        pref_val = getattr(prefs, dim)
        drink_val = float(profile[dim])
        diff = abs(drink_val - pref_val)

        if diff <= CLOSE_THRESHOLD:
            if pref_val >= 4:
                taste_reasons.append(f"High {label} matches your preference")
            elif pref_val <= 2:
                taste_reasons.append(f"Low {label} aligns with your taste")
            else:
                taste_reasons.append(f"{label.capitalize()} closely matches your preference")
        elif diff > FAR_THRESHOLD:
            direction = "higher" if drink_val > pref_val else "lower"
            taste_reasons.append(f"{label.capitalize()} is {direction} than your preference")

    combined = priority_reasons + taste_reasons
    return combined[:4] if combined else ["Good overall match"]


def rank_drinks(
    prefs: RecommendationRequest,
    drinks_with_profiles: list[dict],
    cafes_by_id: dict[str, dict],
) -> list[RecommendationResult]:
    """
    Filter, score, and sort drinks against user preferences.
    Returns a ranked list capped at prefs.limit.
    """
    results: list[RecommendationResult] = []

    for entry in drinks_with_profiles:
        drink = entry
        profile = entry["profile"]
        price_value = drink.get("price")
        price = float(price_value) if price_value is not None else None
        milk_options: list[str] = drink.get("milk_options", [])

        # ── Hard filters ──────────────────────────────────────────────────────
        if prefs.price_max is not None and (price is None or price > prefs.price_max):
            continue

        if prefs.milk_type is not None:
            options_lower = [m.lower() for m in milk_options]
            if prefs.milk_type.lower() not in options_lower:
                continue

        # ── Score ─────────────────────────────────────────────────────────────
        raw_score = _score_drink(prefs, profile)
        match_pct = max(0, min(100, round(raw_score * 100)))

        cafe_id = drink["cafe_id"]
        cafe = cafes_by_id.get(cafe_id, {})

        review_count = int(profile.get("review_count", 0))
        conf_label, conf_score = compute_confidence(review_count)

        taste_snapshot = TasteProfileSnapshot(
            matcha_strength=float(profile["matcha_strength"]),
            sweetness=float(profile["sweetness"]),
            creaminess=float(profile["creaminess"]),
            earthiness=float(profile["earthiness"]),
            bitterness=float(profile["bitterness"]),
            review_count=review_count,
            confidence_label=conf_label,
            confidence_score=conf_score,
        )

        results.append(RecommendationResult(
            drink_id=drink["drink_id"],
            drink_name=drink["name"],
            cafe_id=cafe_id,
            cafe_name=cafe.get("name"),
            price=price,
            milk_options=milk_options,
            taste_profile=taste_snapshot,
            match_score=round(raw_score, 4),
            match_pct=match_pct,
            reasons=_build_reasons(prefs, profile, drink, match_pct),
            confidence_label=conf_label,
            confidence_score=conf_score,
        ))

    # Primary sort: match_pct desc. Tiebreaker: confidence_score desc, then price asc.
    results.sort(
        key=lambda r: (
            -r.match_pct,
            -(r.confidence_score or 0.0),
            r.price if r.price is not None else float("inf"),
        )
    )

    return results[: prefs.limit]
