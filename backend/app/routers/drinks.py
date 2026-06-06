from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services import db
from app.models.drink import Drink
from app.models.taste_profile import TasteProfile, compute_confidence

router = APIRouter(prefix="/drinks", tags=["drinks"])


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


def _item_to_taste_profile(item: dict) -> TasteProfile:
    review_count = int(item.get("review_count", 0))
    conf_label, conf_score = compute_confidence(review_count)
    return TasteProfile(
        drink_id=item["drink_id"],
        matcha_strength=float(item["matcha_strength"]),
        sweetness=float(item["sweetness"]),
        creaminess=float(item["creaminess"]),
        earthiness=float(item["earthiness"]),
        bitterness=float(item["bitterness"]),
        review_count=review_count,
        last_updated=item["last_updated"],
        confidence_label=conf_label,
        confidence_score=conf_score,
    )


@router.get("", response_model=list[Drink])
def list_drinks(cafe_id: Optional[str] = Query(default=None)):
    if cafe_id:
        items = db.query_gsi(gsi_pk_value=f"CAFE#{cafe_id}")
        # GSI returns drinks for a cafe; filter to METADATA items only
        items = [i for i in items if i.get("SK") == "METADATA"]
    else:
        items = db.scan_by_entity_type("DRINK")
    return [_item_to_drink(item) for item in items]


@router.get("/{drink_id}", response_model=Drink)
def get_drink(drink_id: str):
    item = db.get_item(pk=f"DRINK#{drink_id}", sk="METADATA")
    if not item:
        raise HTTPException(status_code=404, detail=f"Drink '{drink_id}' not found")
    return _item_to_drink(item)


@router.get("/{drink_id}/taste-profile", response_model=TasteProfile)
def get_taste_profile(drink_id: str):
    item = db.get_item(pk=f"DRINK#{drink_id}", sk="TASTE_PROFILE")
    if not item:
        raise HTTPException(status_code=404, detail=f"Taste profile for drink '{drink_id}' not found")
    return _item_to_taste_profile(item)
