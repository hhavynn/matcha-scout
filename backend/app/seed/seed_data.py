"""
Seeds the DynamoDB table with fictional sample cafes, drinks, and taste profiles.
ALL DATA IS FICTIONAL and for demo purposes only.

Run after create_tables.py:
  docker compose exec api python -m app.seed.seed_data
"""
import boto3
from decimal import Decimal
from app.core.config import settings

# ── Sample data ──────────────────────────────────────────────────────────────
# Note: All cafes, drinks, prices, and descriptions below are entirely fictional.

CAFES = [
    {
        "id": "cafe-001",
        "name": "Verdant Cup",
        "location": "Portland, OR",
        "address": "412 NW Everett St, Portland, OR 97209",
        "website": "https://example.com/verdantcup",
    },
    {
        "id": "cafe-002",
        "name": "Umami House",
        "location": "Seattle, WA",
        "address": "801 Pike St, Seattle, WA 98101",
        "website": "https://example.com/umamihouse",
    },
    {
        "id": "cafe-003",
        "name": "Shizen Matcha Bar",
        "location": "San Francisco, CA",
        "address": "1023 Valencia St, San Francisco, CA 94110",
        "website": "https://example.com/shizen",
    },
    {
        "id": "cafe-004",
        "name": "Tender Leaf",
        "location": "Austin, TX",
        "address": "256 S Congress Ave, Austin, TX 78704",
        "website": "https://example.com/tenderleaf",
    },
    {
        "id": "cafe-005",
        "name": "Kocha & Co.",
        "location": "Brooklyn, NY",
        "address": "88 Bedford Ave, Brooklyn, NY 11211",
        "website": "https://example.com/kochaco",
    },
]

# Each drink links to a cafe via cafe_id.
# Taste profile fields: matcha_strength, sweetness, creaminess, earthiness, bitterness (all 1.0–5.0)
DRINKS = [
    {
        "id": "drink-001",
        "cafe_id": "cafe-001",
        "name": "Stone Garden Ceremonial",
        "description": "A single-origin ceremonial grade matcha whisked to order. No milk, no sweetener — pure, grassy, and intensely earthy.",
        "price": "6.50",
        "milk_options": ["none"],
        "is_iced": False,
        "is_hot": True,
        "taste": {"matcha_strength": "5.0", "sweetness": "1.0", "creaminess": "1.0", "earthiness": "5.0", "bitterness": "4.5"},
    },
    {
        "id": "drink-002",
        "cafe_id": "cafe-001",
        "name": "Oat Cloud Latte",
        "description": "Verdant Cup's most popular drink. Creamy oat milk steamed to a velvety foam, balanced with a medium-strength matcha base.",
        "price": "7.00",
        "milk_options": ["oat"],
        "is_iced": True,
        "is_hot": True,
        "taste": {"matcha_strength": "3.0", "sweetness": "2.5", "creaminess": "4.5", "earthiness": "2.5", "bitterness": "2.0"},
    },
    {
        "id": "drink-003",
        "cafe_id": "cafe-002",
        "name": "Strawberry Matcha Refresher",
        "description": "Iced matcha layered over housemade strawberry syrup and coconut milk. Sweet, fruity, and Instagram-friendly.",
        "price": "8.00",
        "milk_options": ["coconut"],
        "is_iced": True,
        "is_hot": False,
        "taste": {"matcha_strength": "2.0", "sweetness": "4.5", "creaminess": "3.0", "earthiness": "1.5", "bitterness": "1.0"},
    },
    {
        "id": "drink-004",
        "cafe_id": "cafe-002",
        "name": "Umami Hojicha Blend",
        "description": "A 50/50 blend of roasted hojicha and ceremonial matcha over whole milk. Smoky, earthy, and lightly sweet.",
        "price": "7.50",
        "milk_options": ["whole"],
        "is_iced": True,
        "is_hot": True,
        "taste": {"matcha_strength": "3.5", "sweetness": "2.0", "creaminess": "3.0", "earthiness": "4.5", "bitterness": "3.5"},
    },
    {
        "id": "drink-005",
        "cafe_id": "cafe-003",
        "name": "Beginner's Matcha Latte",
        "description": "Shizen's gateway drink for matcha newcomers. Mild matcha, lots of oat milk, and a touch of vanilla syrup.",
        "price": "6.75",
        "milk_options": ["oat"],
        "is_iced": False,
        "is_hot": True,
        "taste": {"matcha_strength": "1.5", "sweetness": "4.0", "creaminess": "4.5", "earthiness": "1.0", "bitterness": "1.0"},
    },
    {
        "id": "drink-006",
        "cafe_id": "cafe-003",
        "name": "Yuzu Matcha Fizz",
        "description": "Ceremonial matcha shaken with yuzu juice and poured over sparkling water. Tart, bright, and surprisingly refreshing.",
        "price": "8.50",
        "milk_options": ["none"],
        "is_iced": True,
        "is_hot": False,
        "taste": {"matcha_strength": "3.5", "sweetness": "3.0", "creaminess": "1.0", "earthiness": "2.5", "bitterness": "2.0"},
    },
    {
        "id": "drink-007",
        "cafe_id": "cafe-004",
        "name": "Brown Sugar Matcha",
        "description": "Iced matcha latte with a Taiwanese-style brown sugar syrup swirl and fresh whole milk. Rich and caramel-forward.",
        "price": "7.25",
        "milk_options": ["whole"],
        "is_iced": True,
        "is_hot": False,
        "taste": {"matcha_strength": "2.5", "sweetness": "4.5", "creaminess": "3.5", "earthiness": "2.0", "bitterness": "1.5"},
    },
    {
        "id": "drink-008",
        "cafe_id": "cafe-004",
        "name": "High Altitude Ceremonial",
        "description": "Uji ceremonial grade, stone-ground, whisked tableside. Intensely bitter and deeply grassy with a lingering umami finish.",
        "price": "9.00",
        "milk_options": ["none"],
        "is_iced": False,
        "is_hot": True,
        "taste": {"matcha_strength": "5.0", "sweetness": "1.0", "creaminess": "1.0", "earthiness": "5.0", "bitterness": "5.0"},
    },
    {
        "id": "drink-009",
        "cafe_id": "cafe-005",
        "name": "Lavender Matcha Latte",
        "description": "House-made lavender syrup stirred into a creamy oat matcha latte. Floral, mellow, and lightly earthy.",
        "price": "7.75",
        "milk_options": ["oat"],
        "is_iced": True,
        "is_hot": True,
        "taste": {"matcha_strength": "2.0", "sweetness": "3.5", "creaminess": "4.0", "earthiness": "2.0", "bitterness": "1.5"},
    },
    {
        "id": "drink-010",
        "cafe_id": "cafe-005",
        "name": "Kocha Classic",
        "description": "Kocha's signature: culinary-grade matcha with almond milk and agave. Affordable, consistent, and approachable.",
        "price": "5.50",
        "milk_options": ["almond"],
        "is_iced": True,
        "is_hot": False,
        "taste": {"matcha_strength": "2.5", "sweetness": "3.0", "creaminess": "3.0", "earthiness": "2.0", "bitterness": "2.0"},
    },
]


def seed(table):
    now = "2026-06-05T00:00:00"

    for cafe in CAFES:
        item = {
            "PK": f"CAFE#{cafe['id']}",
            "SK": "METADATA",
            "cafe_id": cafe["id"],
            "name": cafe["name"],
            "location": cafe["location"],
            "created_at": now,
        }
        if cafe.get("address"):
            item["address"] = cafe["address"]
        if cafe.get("website"):
            item["website"] = cafe["website"]
        table.put_item(Item=item)
        print(f"  Seeded cafe: {cafe['name']}")

    for drink in DRINKS:
        taste = drink["taste"]
        # Drink METADATA item
        table.put_item(Item={
            "PK": f"DRINK#{drink['id']}",
            "SK": "METADATA",
            # GSI keys so we can query drinks by cafe
            "GSI1PK": f"CAFE#{drink['cafe_id']}",
            "GSI1SK": f"DRINK#{drink['id']}",
            "drink_id": drink["id"],
            "cafe_id": drink["cafe_id"],
            "name": drink["name"],
            "description": drink["description"],
            "price": Decimal(drink["price"]),
            "milk_options": drink["milk_options"],
            "is_iced": drink["is_iced"],
            "is_hot": drink["is_hot"],
            "created_at": now,
        })

        # Taste profile item
        table.put_item(Item={
            "PK": f"DRINK#{drink['id']}",
            "SK": "TASTE_PROFILE",
            "drink_id": drink["id"],
            "matcha_strength": Decimal(taste["matcha_strength"]),
            "sweetness": Decimal(taste["sweetness"]),
            "creaminess": Decimal(taste["creaminess"]),
            "earthiness": Decimal(taste["earthiness"]),
            "bitterness": Decimal(taste["bitterness"]),
            "review_count": 0,
            "last_updated": now,
        })
        print(f"  Seeded drink: {drink['name']}")

    print("\nSeed complete.")


def main():
    db = boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    table = db.Table(settings.dynamodb_table_name)
    print(f"Seeding table '{settings.dynamodb_table_name}'...")
    seed(table)


if __name__ == "__main__":
    main()
