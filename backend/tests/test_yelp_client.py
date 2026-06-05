import os
import sys
from argparse import Namespace
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-west-2")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from app.core.config import settings
from app.ingest import yelp_san_diego
from app.services import db
from app.services.yelp_client import (
    YelpApiKeyMissingError,
    _headers,
    normalize_yelp_business,
    normalize_yelp_review_excerpt,
)


YELP_BUSINESS = {
    "id": "abc 123",
    "name": "Paru Tea Bar",
    "url": "https://www.yelp.com/biz/paru-tea-bar-san-diego",
    "rating": 4.5,
    "review_count": 321,
    "image_url": "https://example.com/image.jpg",
    "categories": [{"alias": "tea", "title": "Tea Rooms"}],
    "coordinates": {"latitude": 32.7157, "longitude": -117.1611},
    "display_phone": "(619) 555-0101",
    "price": "$$",
    "location": {
        "display_address": ["123 Matcha St", "San Diego, CA 92101"],
        "city": "San Diego",
        "state": "CA",
    },
}


def test_normalize_yelp_business_maps_external_metadata():
    cafe = normalize_yelp_business(YELP_BUSINESS, ingested_at="2026-06-05T00:00:00+00:00")

    assert cafe["cafe_id"] == "yelp-abc-123"
    assert cafe["source"] == "yelp"
    assert cafe["external_id"] == "abc 123"
    assert cafe["external_url"].startswith("https://www.yelp.com/")
    assert cafe["rating"] == Decimal("4.5")
    assert cafe["review_count"] == 321
    assert cafe["categories"] == ["Tea Rooms"]
    assert cafe["location"] == "San Diego, CA"


def test_normalize_yelp_review_excerpt_keeps_it_external():
    review = normalize_yelp_review_excerpt(
        {
            "id": "review-1",
            "text": "Great matcha, earthy and smooth.",
            "rating": 5,
            "time_created": "2026-06-05 12:00:00",
            "url": "https://www.yelp.com/biz/example?hrid=review-1",
            "user": {"name": "Ari"},
        },
        ingested_at="2026-06-05T00:00:00+00:00",
    )

    assert review["external_review_id"] == "review-1"
    assert review["source"] == "yelp"
    assert review["excerpt"] == "Great matcha, earthy and smooth."
    assert review["rating"] == Decimal("5")
    assert "raw_text" not in review
    assert "drink_id" not in review


def test_missing_yelp_api_key_produces_clean_error(monkeypatch):
    monkeypatch.setattr(settings, "yelp_api_key", None)

    with pytest.raises(YelpApiKeyMissingError, match="YELP_API_KEY"):
        _headers()


def test_dry_run_does_not_write_to_db(monkeypatch, capsys):
    monkeypatch.setattr(yelp_san_diego, "search_businesses", lambda *args, **kwargs: [YELP_BUSINESS])
    monkeypatch.setattr(yelp_san_diego, "get_business_reviews", lambda business_id: [])

    def fail_write(*args, **kwargs):
        raise AssertionError("dry-run should not write")

    monkeypatch.setattr(yelp_san_diego.db, "upsert_cafe_from_external_source", fail_write)
    args = Namespace(
        limit=1,
        offset=0,
        term="matcha",
        location="San Diego, CA",
        include_reviews=False,
        dry_run=True,
        apply=False,
        local=True,
        no_overwrite=False,
    )

    assert yelp_san_diego.run(args) == 0
    assert "Dry run only" in capsys.readouterr().out


def test_put_external_review_excerpt_uses_external_review_key(monkeypatch):
    writes = []

    class FakeTable:
        def put_item(self, Item):
            writes.append(Item)

    monkeypatch.setattr(db, "get_table", lambda: FakeTable())
    db.put_external_review_excerpt(
        "cafe-123",
        {
            "external_review_id": "review-1",
            "source": "yelp",
            "excerpt": "External Yelp excerpt",
            "ingested_at": "2026-06-05T00:00:00+00:00",
        },
    )

    assert writes[0]["PK"] == "CAFE#cafe-123"
    assert writes[0]["SK"] == "EXTERNAL_REVIEW#YELP#review-1"
    assert not writes[0]["SK"].startswith("REVIEW#")


def test_upsert_preserves_user_owned_fields_with_no_overwrite(monkeypatch):
    existing = {
        "PK": "CAFE#yelp-abc-123",
        "SK": "METADATA",
        "cafe_id": "yelp-abc-123",
        "name": "User Curated Name",
        "location": "San Diego, CA",
        "created_at": "2026-06-01T00:00:00+00:00",
        "source": "yelp",
        "external_id": "abc 123",
    }
    writes = []

    class FakeTable:
        def put_item(self, Item):
            writes.append(Item)

    monkeypatch.setattr(db, "get_cafe_by_external_source", lambda source, external_id: existing)
    monkeypatch.setattr(db, "get_table", lambda: FakeTable())

    db.upsert_cafe_from_external_source(
        {
            "cafe_id": "yelp-abc-123",
            "name": "Yelp Name",
            "location": "San Diego, CA",
            "created_at": "2026-06-05T00:00:00+00:00",
            "source": "yelp",
            "external_id": "abc 123",
            "rating": Decimal("4.5"),
        },
        no_overwrite=True,
    )

    assert writes[0]["name"] == "User Curated Name"
    assert writes[0]["rating"] == Decimal("4.5")


def test_taste_profile_aggregation_queries_only_matcha_scout_review_items(monkeypatch):
    from app.services import aggregator

    captured = {}

    class FakeTable:
        def query(self, KeyConditionExpression):
            captured["expression"] = KeyConditionExpression
            return {"Items": []}

        def put_item(self, Item):
            raise AssertionError("no taste profile should be written when no Matcha Scout reviews are returned")

    monkeypatch.setattr(db, "get_table", lambda: FakeTable())

    aggregator.recalculate_taste_profile("drink-123")

    expression_parts = captured["expression"].get_expression()["values"]
    pk_expression = expression_parts[0].get_expression()
    sk_expression = expression_parts[1].get_expression()

    assert pk_expression["values"][0].name == "PK"
    assert pk_expression["values"][1] == "DRINK#drink-123"
    assert sk_expression["values"][0].name == "SK"
    assert sk_expression["values"][1] == "REVIEW#"
