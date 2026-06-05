from fastapi import APIRouter, HTTPException
from app.services import db
from app.models.cafe import Cafe, ExternalReviewExcerpt

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
def list_cafes():
    items = db.scan_by_entity_type("CAFE")
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
