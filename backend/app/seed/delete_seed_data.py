"""
Deletes all fictional seed cafes, drinks, and associated items from the database.
Works for both local development and production.

Usage:
  # Local Postgres:
  docker compose exec api python -m app.seed.delete_seed_data

  # Production Neon (pass environment variables):
  docker exec -e DATABASE_URL="..." -e DATABASE_ENVIRONMENT="production" \\
    matcha-api python -m app.seed.delete_seed_data
"""
from app.core.config import settings
from app.services import db


def delete_seed_data():
    target_cafes = [
        "CAFE#cafe-001",
        "CAFE#cafe-002",
        "CAFE#cafe-003",
        "CAFE#cafe-004",
        "CAFE#cafe-005",
    ]

    print("Checking database backend...")

    if db.using_postgres():
        table_name = db._safe_table_name()
        print(f"Using PostgreSQL backend (table: '{table_name}').")

        query = f"""
            DELETE FROM {table_name}
            WHERE pk = ANY(%s)
               OR pk LIKE 'DRINK#drink-00%%'
               OR gsi1pk = ANY(%s)
        """
        with db._postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (target_cafes, target_cafes))
                row_count = cursor.rowcount
                print(f"Deleted {row_count} seed records from PostgreSQL.")
        return

    # DynamoDB fallback:
    print("Using DynamoDB backend.")
    table = db.get_table()

    # Find items to delete
    items_to_delete = []

    # 1. Scan for cafes
    for cafe_pk in target_cafes:
        # Get metadata
        items_to_delete.append({"PK": cafe_pk, "SK": "METADATA"})
        # Get external reviews
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": cafe_pk}
        )
        for item in resp.get("Items", []):
            if item.get("SK", "").startswith("EXTERNAL_REVIEW#"):
                items_to_delete.append({"PK": item["PK"], "SK": item["SK"]})

    # 2. Scan for drinks 001 through 010 and their sub-items
    for i in range(1, 11):
        drink_pk = f"DRINK#drink-00{i}"
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": drink_pk}
        )
        for item in resp.get("Items", []):
            items_to_delete.append({"PK": item["PK"], "SK": item["SK"]})

    # Execute batch deletes in DynamoDB
    if not items_to_delete:
        print("No seed items found in DynamoDB.")
        return

    deleted_count = 0
    with table.batch_writer() as batch:
        for item in items_to_delete:
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
            deleted_count += 1

    print(f"Deleted {deleted_count} seed items from DynamoDB.")


if __name__ == "__main__":
    delete_seed_data()
