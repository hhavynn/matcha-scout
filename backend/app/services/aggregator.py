"""
Recalculates a drink's aggregate taste profile from all stored reviews.
Called after every new review is saved.
"""
from decimal import Decimal
from datetime import datetime, timezone
from app.services import db


def recalculate_taste_profile(drink_id: str) -> None:
    if db.using_postgres():
        reviews = db.list_reviews_for_drink(drink_id)
    else:
        table = db.get_table()

        # Preserve the legacy DynamoDB query path while existing local tools
        # and tests are transitioned.
        from boto3.dynamodb.conditions import Key
        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"DRINK#{drink_id}") & Key("SK").begins_with("REVIEW#")
        )
        reviews = response.get("Items", [])

    if not reviews:
        return

    fields = ["parsed_strength", "parsed_sweetness", "parsed_creaminess", "parsed_earthiness", "parsed_bitterness"]
    totals = {f: 0.0 for f in fields}
    count = 0

    for r in reviews:
        # Only count reviews that have all parsed fields
        if all(r.get(f) is not None for f in fields):
            for f in fields:
                totals[f] += float(r[f])
            count += 1

    if count == 0:
        return

    now = datetime.now(timezone.utc).isoformat()
    db.put_item({
        "PK": f"DRINK#{drink_id}",
        "SK": "TASTE_PROFILE",
        "drink_id": drink_id,
        "matcha_strength": Decimal(str(round(totals["parsed_strength"] / count, 2))),
        "sweetness":       Decimal(str(round(totals["parsed_sweetness"] / count, 2))),
        "creaminess":      Decimal(str(round(totals["parsed_creaminess"] / count, 2))),
        "earthiness":      Decimal(str(round(totals["parsed_earthiness"] / count, 2))),
        "bitterness":      Decimal(str(round(totals["parsed_bitterness"] / count, 2))),
        "review_count": count,
        "last_updated": now,
    })
