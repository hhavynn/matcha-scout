import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from boto3.dynamodb.conditions import Key
from app.services import db
from app.services.ai_parser import parse_matcha_review
from app.services.aggregator import recalculate_taste_profile
from app.models.review import ReviewCreate, ReviewResponse, Review

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def submit_review(body: ReviewCreate):
    # Verify the drink exists
    drink = db.get_item(pk=f"DRINK#{body.drink_id}", sk="METADATA")
    if not drink:
        raise HTTPException(status_code=404, detail=f"Drink '{body.drink_id}' not found")

    # Parse review through AI (mock or Gemini)
    parsed = parse_matcha_review(body.raw_text)

    # Build DynamoDB item
    now = datetime.now(timezone.utc)
    review_id = str(uuid.uuid4())
    sk = f"REVIEW#{now.isoformat()}#{review_id}"

    item = {
        "PK": f"DRINK#{body.drink_id}",
        "SK": sk,
        "review_id": review_id,
        "drink_id": body.drink_id,
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
        item["summary"] = parsed.summary
    if parsed.tags:
        item["tags"] = parsed.tags

    db.put_item(item)

    # Recalculate aggregate taste profile
    recalculate_taste_profile(body.drink_id)

    return ReviewResponse(
        id=review_id,
        drink_id=body.drink_id,
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
    )


@router.get("/drinks/{drink_id}/reviews", response_model=list[ReviewResponse])
def list_reviews(drink_id: str):
    # Verify the drink exists
    drink = db.get_item(pk=f"DRINK#{drink_id}", sk="METADATA")
    if not drink:
        raise HTTPException(status_code=404, detail=f"Drink '{drink_id}' not found")

    table = db.get_table()
    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"DRINK#{drink_id}") & Key("SK").begins_with("REVIEW#")
    )
    items = response.get("Items", [])

    return [
        ReviewResponse(
            id=item["review_id"],
            drink_id=item["drink_id"],
            raw_text=item["raw_text"],
            parsed_strength=int(item["parsed_strength"]),
            parsed_sweetness=int(item["parsed_sweetness"]),
            parsed_creaminess=int(item["parsed_creaminess"]),
            parsed_earthiness=int(item["parsed_earthiness"]),
            parsed_bitterness=int(item["parsed_bitterness"]),
            confidence=float(item["confidence"]),
            summary=item.get("summary"),
            tags=item.get("tags"),
            submitted_at=datetime.fromisoformat(item["submitted_at"]),
        )
        for item in items
    ]
