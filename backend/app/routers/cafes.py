import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from app.services import db
from app.models.cafe import Cafe, ExternalReviewExcerpt
from app.models.drink import Drink, DrinkCreate
from app.models.review import ReviewCreate, ReviewResponse
from app.services.ai_parser import parse_matcha_review
from app.services.aggregator import recalculate_taste_profile
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/cafes", tags=["cafes"])


def _item_to_cafe(item: dict) -> Cafe:
    return Cafe(
        id=item["cafe_id"],
        name=item["name"],
        location=item["location"],
        address=item.get("address"),
        website=item.get("website"),
        created_at=item["created_at"],
        source=item.get("source"),
        external_id=item.get("external_id"),
        external_url=item.get("external_url"),
        rating=float(item["rating"]) if item.get("rating") is not None else None,
        review_count=int(item["review_count"]) if item.get("review_count") is not None else None,
        image_url=item.get("image_url"),
        categories=item.get("categories"),
        latitude=float(item["latitude"]) if item.get("latitude") is not None else None,
        longitude=float(item["longitude"]) if item.get("longitude") is not None else None,
        phone=item.get("phone"),
        price=item.get("price"),
        last_ingested_at=item.get("last_ingested_at"),
        region_key=item.get("region_key"),
        region_label=item.get("region_label"),
    )


def _item_to_external_review(item: dict) -> ExternalReviewExcerpt:
    return ExternalReviewExcerpt(
        id=item["external_review_id"],
        cafe_id=item["cafe_id"],
        source=item["source"],
        excerpt=item["excerpt"],
        rating=float(item["rating"]) if item.get("rating") is not None else None,
        author_name=item.get("author_name"),
        time_created=item.get("time_created"),
        external_url=item.get("external_url"),
        ingested_at=item["ingested_at"],
    )


@router.get("", response_model=list[Cafe])
def list_cafes(region_key: Optional[str] = Query(default=None)):
    items = db.scan_by_entity_type("CAFE")
    if region_key:
        items = [i for i in items if i.get("region_key") == region_key]
    return [_item_to_cafe(item) for item in items]


@router.get("/{cafe_id}/external-reviews", response_model=list[ExternalReviewExcerpt])
def list_external_reviews(cafe_id: str):
    cafe = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not cafe:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")
    return [_item_to_external_review(item) for item in db.list_external_review_excerpts(cafe_id)]


@router.get("/{cafe_id}", response_model=Cafe)
def get_cafe(cafe_id: str):
    item = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not item:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")
    return _item_to_cafe(item)


def _item_to_drink(item: dict) -> Drink:
    return Drink(
        id=item["drink_id"],
        cafe_id=item["cafe_id"],
        name=item["name"],
        description=item.get("description", ""),
        price=float(item.get("price", 0)),
        milk_options=item.get("milk_options", []),
        is_iced=item.get("is_iced"),
        is_hot=item.get("is_hot"),
        image_url=item.get("image_url"),
        created_at=item["created_at"],
        source=item.get("source"),
        verification_status=item.get("verification_status"),
        submitted_at=item.get("submitted_at"),
        submitted_by_session=item.get("submitted_by_session"),
    )


def _create_drink_item(cafe_id: str, body: DrinkCreate) -> dict:
    """Build and store a new drink + neutral taste profile. Returns the raw item."""
    drink_id = f"drink-{uuid.uuid4()}"
    now = datetime.now(timezone.utc).isoformat()
    milk_options = [m.lower().strip() for m in (body.milk_options or [])]

    drink_item = {
        "PK": f"DRINK#{drink_id}",
        "SK": "METADATA",
        "GSI1PK": f"CAFE#{cafe_id}",
        "GSI1SK": f"DRINK#{drink_id}",
        "drink_id": drink_id,
        "cafe_id": cafe_id,
        "name": body.name,
        "description": body.description or "",
        "price": Decimal(str(body.price)) if body.price is not None else Decimal("0"),
        "milk_options": milk_options,
        "source": "user_submitted",
        "verification_status": "unverified",
        "submitted_at": now,
        "created_at": now,
    }
    if body.is_iced is not None:
        drink_item["is_iced"] = body.is_iced
    if body.is_hot is not None:
        drink_item["is_hot"] = body.is_hot
    db.put_item(drink_item)

    # Neutral taste profile — review_count 0 means "unrated" confidence
    db.put_item({
        "PK": f"DRINK#{drink_id}",
        "SK": "TASTE_PROFILE",
        "drink_id": drink_id,
        "matcha_strength": Decimal("3.0"),
        "sweetness": Decimal("3.0"),
        "creaminess": Decimal("3.0"),
        "earthiness": Decimal("3.0"),
        "bitterness": Decimal("3.0"),
        "review_count": 0,
        "last_updated": now,
    })

    return drink_item


@router.get("/{cafe_id}/drinks", response_model=list[Drink])
def list_cafe_drinks(cafe_id: str):
    cafe = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not cafe:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")
    items = db.query_gsi(gsi_pk_value=f"CAFE#{cafe_id}")
    return [_item_to_drink(i) for i in items if i.get("SK") == "METADATA"]


@router.post("/{cafe_id}/drinks", response_model=Drink, status_code=201)
def create_cafe_drink(cafe_id: str, body: DrinkCreate):
    cafe = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not cafe:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")
    item = _create_drink_item(cafe_id, body)
    return _item_to_drink(item)


class DrinkWithReviewCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    milk_options: Optional[list[str]] = None
    is_iced: Optional[bool] = None
    is_hot: Optional[bool] = None
    raw_text: str


class DrinkWithReviewResponse(BaseModel):
    drink: Drink
    review: ReviewResponse


@router.post("/{cafe_id}/drinks-with-review", response_model=DrinkWithReviewResponse, status_code=201)
def create_cafe_drink_with_review(cafe_id: str, body: DrinkWithReviewCreate):
    cafe = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not cafe:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")

    drink_create = DrinkCreate(
        name=body.name,
        description=body.description,
        price=body.price,
        milk_options=body.milk_options,
        is_iced=body.is_iced,
        is_hot=body.is_hot,
    )
    drink_item = _create_drink_item(cafe_id, drink_create)
    drink_id = drink_item["drink_id"]

    parsed = parse_matcha_review(body.raw_text)
    now = datetime.now(timezone.utc)
    review_id = str(uuid.uuid4())
    sk = f"REVIEW#{now.isoformat()}#{review_id}"
    review_item = {
        "PK": f"DRINK#{drink_id}",
        "SK": sk,
        "review_id": review_id,
        "drink_id": drink_id,
        "raw_text": body.raw_text,
        "parsed_strength":   parsed.matcha_strength,
        "parsed_sweetness":  parsed.sweetness,
        "parsed_creaminess": parsed.creaminess,
        "parsed_earthiness": parsed.earthiness,
        "parsed_bitterness": parsed.bitterness,
        "confidence":        Decimal(str(parsed.confidence)),
        "submitted_at":      now.isoformat(),
    }
    if parsed.summary:
        review_item["summary"] = parsed.summary
    if parsed.tags:
        review_item["tags"] = parsed.tags
    db.put_item(review_item)
    recalculate_taste_profile(drink_id)

    return DrinkWithReviewResponse(
        drink=_item_to_drink(drink_item),
        review=ReviewResponse(
            id=review_id,
            drink_id=drink_id,
            raw_text=body.raw_text,
            parsed_strength=parsed.matcha_strength,
            parsed_sweetness=parsed.sweetness,
            parsed_creaminess=parsed.creaminess,
            parsed_earthiness=parsed.earthiness,
            parsed_bitterness=parsed.bitterness,
            confidence=parsed.confidence,
            summary=parsed.summary,
            tags=parsed.tags,
            submitted_at=now,
        ),
    )
