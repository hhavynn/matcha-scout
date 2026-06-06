from unittest.mock import patch

from fastapi.testclient import TestClient


def _make_test_client():
    from app.main import app

    return TestClient(app)


def _drink(
    drink_id: str,
    cafe_id: str,
    name: str,
    *,
    source: str = "admin_curated",
    verification_status: str = "admin_verified",
):
    return {
        "PK": f"DRINK#{drink_id}",
        "SK": "METADATA",
        "entity_type": "DRINK",
        "drink_id": drink_id,
        "cafe_id": cafe_id,
        "name": name,
        "description": f"{name} description",
        "price": "7.50",
        "milk_options": ["oat"],
        "is_iced": True,
        "is_hot": False,
        "created_at": "2026-06-05T00:00:00",
        "source": source,
        "verification_status": verification_status,
    }


def _profile(drink_id: str, review_count: int):
    return {
        "PK": f"DRINK#{drink_id}",
        "SK": "TASTE_PROFILE",
        "drink_id": drink_id,
        "matcha_strength": "3.0",
        "sweetness": "3.0",
        "creaminess": "3.0",
        "earthiness": "3.0",
        "bitterness": "3.0",
        "review_count": review_count,
        "last_updated": "2026-06-05T00:00:00",
    }


CAFES = {
    "cafe-a": {
        "PK": "CAFE#cafe-a",
        "SK": "METADATA",
        "cafe_id": "cafe-a",
        "name": "Aster Matcha",
        "location": "San Diego, CA",
        "region_key": "san-diego",
        "region_label": "San Diego",
        "created_at": "2026-06-05T00:00:00",
    },
    "cafe-b": {
        "PK": "CAFE#cafe-b",
        "SK": "METADATA",
        "cafe_id": "cafe-b",
        "name": "Briar Tea",
        "location": "Orange County, CA",
        "region_key": "orange-county",
        "region_label": "Orange County",
        "created_at": "2026-06-05T00:00:00",
    },
}


def test_review_targets_return_verified_unrated_drinks_first():
    client = _make_test_client()
    drinks = [
        _drink("drink-low", "cafe-a", "One Review Matcha"),
        _drink("drink-unrated", "cafe-a", "Fresh Matcha"),
        _drink("drink-user", "cafe-a", "Unverified Matcha", source="user_submitted", verification_status="unverified"),
    ]
    profiles = [_profile("drink-low", 1), _profile("drink-unrated", 0), _profile("drink-user", 0)]

    with (
        patch("app.routers.drinks.db.scan_by_entity_type", return_value=drinks),
        patch("app.routers.drinks.db.scan_by_sk", return_value=profiles),
        patch("app.routers.drinks.db.get_all_cafes_by_id", return_value=CAFES),
    ):
        resp = client.get("/drinks/review-targets")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert [item["id"] for item in data] == ["drink-unrated", "drink-low"]
    assert data[0]["confidence_label"] == "unrated"
    assert data[0]["review_count"] == 0


def test_review_targets_filter_by_region_key():
    client = _make_test_client()
    drinks = [
        _drink("drink-sd", "cafe-a", "SD Matcha"),
        _drink("drink-oc", "cafe-b", "OC Matcha"),
    ]
    profiles = [_profile("drink-sd", 0), _profile("drink-oc", 0)]

    with (
        patch("app.routers.drinks.db.scan_by_entity_type", return_value=drinks),
        patch("app.routers.drinks.db.scan_by_sk", return_value=profiles),
        patch("app.routers.drinks.db.get_all_cafes_by_id", return_value=CAFES),
    ):
        resp = client.get("/drinks/review-targets?region_key=san-diego")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "drink-sd"
    assert data[0]["region_key"] == "san-diego"


def test_review_targets_exclude_high_review_count():
    client = _make_test_client()
    drinks = [
        _drink("drink-new", "cafe-a", "New Matcha"),
        _drink("drink-reviewed", "cafe-a", "Reviewed Matcha"),
    ]
    profiles = [_profile("drink-new", 0), _profile("drink-reviewed", 2)]

    with (
        patch("app.routers.drinks.db.scan_by_entity_type", return_value=drinks),
        patch("app.routers.drinks.db.scan_by_sk", return_value=profiles),
        patch("app.routers.drinks.db.get_all_cafes_by_id", return_value=CAFES),
    ):
        resp = client.get("/drinks/review-targets?max_review_count=1")

    assert resp.status_code == 200
    assert [item["id"] for item in resp.json()] == ["drink-new"]


def test_review_targets_include_cafe_info_and_never_write():
    client = _make_test_client()
    drinks = [_drink("drink-a", "cafe-a", "Cafe Info Matcha")]
    profiles = [_profile("drink-a", 0)]

    with (
        patch("app.routers.drinks.db.scan_by_entity_type", return_value=drinks),
        patch("app.routers.drinks.db.scan_by_sk", return_value=profiles),
        patch("app.routers.drinks.db.get_all_cafes_by_id", return_value=CAFES),
        patch("app.routers.drinks.db.put_item") as put_item,
    ):
        resp = client.get("/drinks/review-targets")

    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["cafe_name"] == "Aster Matcha"
    assert data[0]["cafe_location"] == "San Diego, CA"
    assert data[0]["region_label"] == "San Diego"
    put_item.assert_not_called()


def test_review_targets_confidence_ignores_external_review_excerpts():
    client = _make_test_client()
    drinks = [_drink("drink-a", "cafe-a", "External Excerpt Matcha")]
    profiles = [_profile("drink-a", 0)]

    with (
        patch("app.routers.drinks.db.scan_by_entity_type", return_value=drinks),
        patch("app.routers.drinks.db.scan_by_sk", return_value=profiles) as scan_by_sk,
        patch("app.routers.drinks.db.get_all_cafes_by_id", return_value=CAFES),
    ):
        resp = client.get("/drinks/review-targets")

    assert resp.status_code == 200
    scan_by_sk.assert_called_once_with("TASTE_PROFILE")
    data = resp.json()
    assert data[0]["review_count"] == 0
    assert data[0]["confidence_label"] == "unrated"
