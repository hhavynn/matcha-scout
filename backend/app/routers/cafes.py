from fastapi import APIRouter, HTTPException
from app.services import db
from app.models.cafe import Cafe

router = APIRouter(prefix="/cafes", tags=["cafes"])


def _item_to_cafe(item: dict) -> Cafe:
    return Cafe(
        id=item["cafe_id"],
        name=item["name"],
        location=item["location"],
        address=item.get("address"),
        website=item.get("website"),
        created_at=item["created_at"],
    )


@router.get("", response_model=list[Cafe])
def list_cafes():
    items = db.scan_by_entity_type("CAFE")
    return [_item_to_cafe(item) for item in items]


@router.get("/{cafe_id}", response_model=Cafe)
def get_cafe(cafe_id: str):
    item = db.get_item(pk=f"CAFE#{cafe_id}", sk="METADATA")
    if not item:
        raise HTTPException(status_code=404, detail=f"Cafe '{cafe_id}' not found")
    return _item_to_cafe(item)
