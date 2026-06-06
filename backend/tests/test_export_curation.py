"""
Tests for the curation target export script.

No Yelp calls, no real DynamoDB writes. All cafe data is mocked.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8001")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "matcha_scout")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")

from app.ingest.export_curation_targets import (
    apply_filters,
    curation_priority_score,
    fetch_cafes,
    write_json,
    write_markdown,
)


# ── Sample cafe fixtures ───────────────────────────────────────────────────────

def _make_cafe(
    cafe_id: str,
    name: str,
    region: str = "san-diego",
    rating: float = 4.0,
    review_count: int = 200,
    categories: list[str] | None = None,
    external_url: str | None = None,
    address: str = "123 Main St, San Diego, CA",
) -> dict:
    return {
        "cafe_id": cafe_id,
        "name": name,
        "region_key": region,
        "region_label": "San Diego" if region == "san-diego" else "Orange County",
        "location": "San Diego, CA" if region == "san-diego" else "Irvine, CA",
        "address": address,
        "rating": str(rating),
        "review_count": str(review_count),
        "categories": categories or ["Coffee & Tea"],
        "external_url": external_url,
        "external_id": f"yelp-{cafe_id}",
        "source": "yelp",
    }


MATCHA_CAFE = _make_cafe(
    "cafe-matcha", "Matcha Cafe Maiko",
    categories=["Coffee & Tea", "Ice Cream & Frozen Yogurt", "Bubble Tea"],
    rating=4.2, review_count=853,
)
TEA_HOUSE = _make_cafe(
    "cafe-tea", "Yun Tea House",
    categories=["Tea Rooms", "Coffee & Tea"],
    rating=4.8, review_count=3500,
)
GENERIC_COFFEE = _make_cafe(
    "cafe-coffee", "Plain Coffee Shop",
    categories=["Coffee & Tea"],
    rating=3.8, review_count=100,
)
OC_CAFE = _make_cafe(
    "cafe-oc", "Junbi Matcha & Tea",
    region="orange-county",
    categories=["Bubble Tea", "Coffee & Tea"],
    rating=4.1, review_count=416,
)


# ── curation_priority_score ───────────────────────────────────────────────────

def test_matcha_in_name_scores_higher_than_generic():
    assert curation_priority_score(MATCHA_CAFE) > curation_priority_score(GENERIC_COFFEE)


def test_tea_rooms_category_boosts_score():
    tea_rooms = _make_cafe("c-tea", "A Cafe", categories=["Tea Rooms"])
    plain = _make_cafe("c-plain", "A Cafe", categories=["Coffee & Tea"])
    assert curation_priority_score(tea_rooms) > curation_priority_score(plain)


def test_popular_cafe_scores_higher_than_obscure_with_same_name():
    popular = _make_cafe("popular", "Matcha Place", rating=4.5, review_count=1000)
    obscure = _make_cafe("obscure", "Matcha Place", rating=3.0, review_count=5)
    assert curation_priority_score(popular) > curation_priority_score(obscure)


def test_empty_categories_does_not_crash():
    cafe = _make_cafe("c-empty", "Unnamed", categories=None)
    score = curation_priority_score(cafe)
    assert isinstance(score, float)


def test_matcha_keyword_in_name_gives_large_boost():
    with_matcha = _make_cafe("c1", "Matcha Shop", categories=["Coffee & Tea"])
    without = _make_cafe("c2", "Beverage Shop", categories=["Coffee & Tea"])
    assert curation_priority_score(with_matcha) > curation_priority_score(without) + 5


# ── apply_filters ─────────────────────────────────────────────────────────────

def test_min_rating_filters_below_threshold():
    cafes = [MATCHA_CAFE, TEA_HOUSE, GENERIC_COFFEE]  # ratings: 4.2, 4.8, 3.8
    result = apply_filters(cafes, min_rating=4.0, sort="relevance", limit=None)
    ids = [c["cafe_id"] for c in result]
    assert "cafe-coffee" not in ids


def test_limit_caps_output():
    cafes = [MATCHA_CAFE, TEA_HOUSE, GENERIC_COFFEE, OC_CAFE]
    result = apply_filters(cafes, min_rating=None, sort="relevance", limit=2)
    assert len(result) == 2


def test_sort_by_rating_descending():
    cafes = [MATCHA_CAFE, GENERIC_COFFEE, TEA_HOUSE]  # 4.2, 3.8, 4.8
    result = apply_filters(cafes, min_rating=None, sort="rating", limit=None)
    ratings = [float(c["rating"]) for c in result]
    assert ratings == sorted(ratings, reverse=True)


def test_sort_by_review_count_descending():
    cafes = [MATCHA_CAFE, GENERIC_COFFEE, TEA_HOUSE]
    result = apply_filters(cafes, min_rating=None, sort="review_count", limit=None)
    counts = [int(c["review_count"]) for c in result]
    assert counts == sorted(counts, reverse=True)


def test_sort_by_relevance_puts_matcha_first():
    cafes = [GENERIC_COFFEE, MATCHA_CAFE]
    result = apply_filters(cafes, min_rating=None, sort="relevance", limit=None)
    assert result[0]["cafe_id"] == "cafe-matcha"


# ── fetch_cafes region filtering ──────────────────────────────────────────────

def test_fetch_cafes_filters_by_region():
    all_cafes = [MATCHA_CAFE, TEA_HOUSE, OC_CAFE]
    with patch("app.ingest.export_curation_targets.db.scan_by_entity_type", return_value=all_cafes):
        result = fetch_cafes("san-diego", "local")
    assert all(c["region_key"] == "san-diego" for c in result)
    assert "cafe-oc" not in [c["cafe_id"] for c in result]


def test_fetch_cafes_all_returns_all_regions():
    all_cafes = [MATCHA_CAFE, OC_CAFE, GENERIC_COFFEE]
    with patch("app.ingest.export_curation_targets.db.scan_by_entity_type", return_value=all_cafes):
        result = fetch_cafes("all", "local")
    assert len(result) == 3


def test_fetch_cafes_does_not_write_to_db():
    with patch("app.ingest.export_curation_targets.db.scan_by_entity_type", return_value=[]) as mock_scan:
        with patch("app.ingest.export_curation_targets.db.put_item") as mock_put:
            fetch_cafes("san-diego", "local")
    mock_put.assert_not_called()


# ── write_markdown ────────────────────────────────────────────────────────────

def test_markdown_output_contains_required_fields(tmp_path):
    output = tmp_path / "test.local.md"
    cafes_with_url = [
        {**MATCHA_CAFE, "external_url": "https://yelp.com/biz/matcha-cafe-maiko"},
        TEA_HOUSE,
    ]
    write_markdown(cafes_with_url, output, "san-diego", "local")
    content = output.read_text()
    assert "Matcha Cafe Maiko" in content
    assert "Yun Tea House" in content
    assert "cafe_id" in content
    assert "Yelp URL" in content
    assert "Source/external_id" in content
    assert "Verified drinks" in content
    assert "Verification notes" in content
    assert "do not commit" in content.lower() or "gitignored" in content.lower()


def test_markdown_does_not_write_to_dynamodb(tmp_path):
    output = tmp_path / "test.local.md"
    with patch("app.ingest.export_curation_targets.db.put_item") as mock_put:
        write_markdown([MATCHA_CAFE], output, "san-diego", "local")
    mock_put.assert_not_called()


# ── write_json ────────────────────────────────────────────────────────────────

def test_json_output_is_valid_json(tmp_path):
    output = tmp_path / "test.local.json"
    write_json([MATCHA_CAFE, OC_CAFE], output, "all", "local")
    data = json.loads(output.read_text())
    assert data["count"] == 2
    assert len(data["cafes"]) == 2


def test_json_output_contains_priority_score(tmp_path):
    output = tmp_path / "test.local.json"
    write_json([MATCHA_CAFE], output, "san-diego", "local")
    data = json.loads(output.read_text())
    assert "curation_priority_score" in data["cafes"][0]
    assert data["cafes"][0]["source"] == "yelp"
    assert data["cafes"][0]["curation_priority_score"] > 0


def test_json_output_has_empty_verified_drinks_list(tmp_path):
    output = tmp_path / "test.local.json"
    write_json([MATCHA_CAFE], output, "san-diego", "local")
    data = json.loads(output.read_text())
    assert data["cafes"][0]["verified_drinks"] == []


# ── run() integration (no real DynamoDB) ─────────────────────────────────────

def test_run_generates_markdown_file(tmp_path):
    from app.ingest.export_curation_targets import run

    out_path = tmp_path / "my-test.local.md"

    class FakeArgs:
        region = "san-diego"
        source = "local"
        output = None  # set below
        limit = 2
        sort = "relevance"
        min_rating = None
        format = "markdown"

    FakeArgs.output = str(out_path)

    with patch("app.ingest.export_curation_targets.db.scan_by_entity_type",
               return_value=[MATCHA_CAFE, GENERIC_COFFEE]):
        code = run(FakeArgs())

    assert code == 0
    assert out_path.exists()
    content = out_path.read_text()
    assert "Matcha Cafe Maiko" in content


def test_run_returns_nonzero_when_no_cafes(tmp_path):
    from app.ingest.export_curation_targets import run

    out_path = tmp_path / "my-empty.local.md"

    class FakeArgs:
        region = "san-diego"
        source = "local"
        output = None  # set below
        limit = None
        sort = "relevance"
        min_rating = None
        format = "markdown"

    FakeArgs.output = str(out_path)

    with patch("app.ingest.export_curation_targets.db.scan_by_entity_type", return_value=[]):
        code = run(FakeArgs())

    assert code != 0
