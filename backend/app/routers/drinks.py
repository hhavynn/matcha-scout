from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services import db
from app.models.drink import Drink, ReviewTargetDrink
from app.models.taste_profile import TasteProfile, compute_confidence

router = APIRouter(prefix="/drinks", tags=["drinks"])

VERIFIED_DRINK_STATUSES = {"admin_curated", "admin_verified"}
VERIFIED_DRINK_SOURCES = {"admin_curated"}


def _item_to_drink(item: dict) -> Drink:
    return Drink(
        id=item["drink_id"],
        cafe_id=item["cafe_id"],
        name=item["name"],
        description=item.get("description", ""),
        price=float(item["price"]) if item.get("price") is not None else None,
        milk_options=item.get("milk_options", []),
        is_iced=item.get("is_iced"),
        is_hot=item.get("is_hot"),
        image_url=item.get("image_url"),
        created_at=item["created_at"],
        source=item.get("source"),
        verification_status=item.get("verification_status"),
        verification_source=item.get("verification_source"),
        verification_url=item.get("verification_url"),
        verification_notes=item.get("verification_notes"),
        verified_at=item.get("verified_at"),
        catalog_status=item.get("catalog_status"),
        exclusion_reason=item.get("exclusion_reason"),
        excluded_at=item.get("excluded_at"),
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


def _is_verified_review_target(item: dict) -> bool:
    return (
        item.get("source") in VERIFIED_DRINK_SOURCES
        or item.get("verification_status") in VERIFIED_DRINK_STATUSES
    )


def _profile_by_drink_id() -> dict[str, dict]:
    return {
        item["drink_id"]: item
        for item in db.scan_by_sk("TASTE_PROFILE")
        if item.get("drink_id")
    }


def _review_target_sort_key(target: ReviewTargetDrink) -> tuple[int, int, str, str]:
    verified_rank = 0 if _is_verified_review_target(target.model_dump()) else 1
    return (
        target.review_count,
        verified_rank,
        target.cafe_name.casefold(),
        target.name.casefold(),
    )


@router.get("", response_model=list[Drink])
def list_drinks(cafe_id: Optional[str] = Query(default=None)):
    if cafe_id:
        items = db.query_gsi(gsi_pk_value=f"CAFE#{cafe_id}")
        # GSI returns drinks for a cafe; filter to METADATA items only
        items = [
            i for i in items
            if i.get("SK") == "METADATA" and db.is_catalog_visible(i)
        ]
    else:
        items = [
            i for i in db.scan_by_entity_type("DRINK")
            if db.is_catalog_visible(i)
        ]
    return [_item_to_drink(item) for item in items]


@router.get("/review-targets", response_model=list[ReviewTargetDrink])
def list_review_targets(
    region_key: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    max_review_count: int = Query(default=1, ge=0, le=100),
):
    drinks = db.scan_by_entity_type("DRINK")
    profiles = _profile_by_drink_id()
    cafes = db.get_all_cafes_by_id()
    targets = []

    for item in drinks:
        if not db.is_catalog_visible(item):
            continue
        if not _is_verified_review_target(item):
            continue

        cafe = cafes.get(item.get("cafe_id"))
        if not cafe:
            continue
        if region_key and cafe.get("region_key") != region_key:
            continue

        profile = profiles.get(item["drink_id"], {})
        review_count = int(profile.get("review_count", 0))
        if review_count > max_review_count:
            continue

        confidence_label, confidence_score = compute_confidence(review_count)
        drink = _item_to_drink(item)
        targets.append(
            ReviewTargetDrink(
                **drink.model_dump(),
                cafe_name=cafe.get("name", ""),
                cafe_location=cafe.get("location"),
                region_key=cafe.get("region_key"),
                region_label=cafe.get("region_label"),
                review_count=review_count,
                confidence_label=confidence_label,
                confidence_score=confidence_score,
            )
        )

    targets.sort(key=_review_target_sort_key)
    return targets[:limit]


@router.get("/{drink_id}", response_model=Drink)
def get_drink(drink_id: str):
    item = db.get_item(pk=f"DRINK#{drink_id}", sk="METADATA")
    if not item or not db.is_catalog_visible(item):
        raise HTTPException(status_code=404, detail=f"Drink '{drink_id}' not found")
    return _item_to_drink(item)


@router.get("/{drink_id}/taste-profile", response_model=TasteProfile)
def get_taste_profile(drink_id: str):
    item = db.get_item(pk=f"DRINK#{drink_id}", sk="TASTE_PROFILE")
    if not item:
        raise HTTPException(status_code=404, detail=f"Taste profile for drink '{drink_id}' not found")
    return _item_to_taste_profile(item)
