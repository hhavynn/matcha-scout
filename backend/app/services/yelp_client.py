from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import requests

from app.core.config import settings


class YelpApiKeyMissingError(RuntimeError):
    pass


class YelpApiError(RuntimeError):
    pass


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "unknown"


def _headers() -> dict[str, str]:
    if not settings.yelp_api_key:
        raise YelpApiKeyMissingError(
            "YELP_API_KEY is not configured. Add it to local .env before running Yelp ingestion."
        )
    return {"Authorization": f"Bearer {settings.yelp_api_key}", "Accept": "application/json"}


def _yelp_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{settings.yelp_api_base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=10)
    except requests.RequestException as exc:
        raise YelpApiError(f"Yelp API request failed: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text[:300]
        raise YelpApiError(f"Yelp API returned HTTP {response.status_code}: {detail}")

    try:
        return response.json()
    except ValueError as exc:
        raise YelpApiError("Yelp API returned invalid JSON") from exc


def search_san_diego_matcha_businesses(limit: int, offset: int = 0) -> list[dict[str, Any]]:
    return search_businesses(
        term=settings.yelp_default_term,
        location=settings.yelp_default_location,
        limit=limit,
        offset=offset,
    )


def search_businesses(
    term: str,
    location: str,
    limit: int,
    offset: int = 0,
) -> list[dict[str, Any]]:
    payload = _yelp_get(
        "/businesses/search",
        {
            "term": term,
            "location": location,
            "limit": min(max(limit, 1), 50),
            "offset": max(offset, 0),
            "categories": "cafes,coffee,tea,bubbletea",
            "sort_by": "best_match",
        },
    )
    return payload.get("businesses", [])


def get_business_details(business_id: str) -> dict[str, Any]:
    return _yelp_get(f"/businesses/{business_id}")


def get_business_reviews(business_id: str) -> list[dict[str, Any]]:
    payload = _yelp_get(f"/businesses/{business_id}/reviews")
    # Yelp Fusion exposes only up to 3 review excerpts. Keep that limitation explicit.
    return payload.get("reviews", [])[:3]


def normalize_yelp_business(
    business: dict[str, Any],
    *,
    location_label: str | None = None,
    ingested_at: str | None = None,
) -> dict[str, Any]:
    now = ingested_at or datetime.now(timezone.utc).isoformat()
    yelp_id = business["id"]
    location = business.get("location") or {}
    coordinates = business.get("coordinates") or {}
    categories = [
        category.get("title") or category.get("alias")
        for category in business.get("categories", [])
        if category.get("title") or category.get("alias")
    ]

    display_address = location.get("display_address") or []
    city = location.get("city")
    state = location.get("state")
    derived_location = ", ".join(part for part in [city, state] if part)

    item: dict[str, Any] = {
        "cafe_id": f"yelp-{_slug(yelp_id)}",
        "name": business.get("name") or "Unnamed Yelp business",
        "location": derived_location or location_label or settings.yelp_default_location,
        "address": ", ".join(display_address) or None,
        "website": business.get("url"),
        "created_at": now,
        "source": "yelp",
        "external_id": yelp_id,
        "external_url": business.get("url"),
        "rating": Decimal(str(business["rating"])) if business.get("rating") is not None else None,
        "review_count": int(business["review_count"]) if business.get("review_count") is not None else None,
        "image_url": business.get("image_url") or None,
        "categories": categories or None,
        "latitude": Decimal(str(coordinates["latitude"])) if coordinates.get("latitude") is not None else None,
        "longitude": Decimal(str(coordinates["longitude"])) if coordinates.get("longitude") is not None else None,
        "phone": business.get("display_phone") or business.get("phone") or None,
        "price": business.get("price") or None,
        "last_ingested_at": now,
    }
    return {key: value for key, value in item.items() if value is not None}


def normalize_yelp_review_excerpt(
    review: dict[str, Any],
    *,
    index: int = 0,
    ingested_at: str | None = None,
) -> dict[str, Any]:
    now = ingested_at or datetime.now(timezone.utc).isoformat()
    user = review.get("user") or {}
    review_id = review.get("id") or f"excerpt-{index}"
    item: dict[str, Any] = {
        "external_review_id": str(review_id),
        "source": "yelp",
        "excerpt": review.get("text") or "",
        "rating": Decimal(str(review["rating"])) if review.get("rating") is not None else None,
        "author_name": user.get("name") or None,
        "time_created": review.get("time_created") or None,
        "external_url": review.get("url") or None,
        "ingested_at": now,
    }
    return {key: value for key, value in item.items() if value is not None}
