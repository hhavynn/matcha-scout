from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key, Attr
from app.core.config import settings


def using_postgres() -> bool:
    return settings.database_backend == "postgres"


def _postgres_connection():
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence.")

    import psycopg
    from psycopg.rows import dict_row

    # Neon provides a pooled endpoint for serverless clients. Disabling
    # automatic prepared statements keeps the client compatible with
    # transaction-pooling behavior.
    return psycopg.connect(
        settings.database_url,
        autocommit=True,
        prepare_threshold=None,
        row_factory=dict_row,
    )


def _safe_table_name() -> str:
    table_name = settings.database_table_name
    if not table_name.replace("_", "").isalnum():
        raise ValueError("DATABASE_TABLE_NAME may contain only letters, numbers, and underscores.")
    return table_name


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def initialize_database() -> None:
    """Create the PostgreSQL item table and access-pattern indexes."""
    if not using_postgres():
        return

    table_name = _safe_table_name()
    with _postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    pk TEXT NOT NULL,
                    sk TEXT NOT NULL,
                    gsi1pk TEXT,
                    gsi1sk TEXT,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (pk, sk)
                )
                """
            )
            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {table_name}_gsi1_idx
                ON {table_name} (gsi1pk, gsi1sk)
                WHERE gsi1pk IS NOT NULL
                """
            )
            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {table_name}_sk_idx
                ON {table_name} (sk)
                """
            )


def get_dynamodb_resource():
    """
    Build a boto3 DynamoDB resource that works in both environments:

    Local dev (Docker):
        DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000  (set in .env)
        AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY set to any non-empty value
        → passes explicit endpoint + credentials to reach DynamoDB Local

    AWS Lambda:
        DYNAMODB_ENDPOINT_URL unset (None)
        → boto3 uses its credential provider chain, which automatically picks up
          the Lambda IAM role credentials (including AWS_SESSION_TOKEN).
          IMPORTANT: never pass AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
          explicitly in Lambda — Lambda temporary credentials require AWS_SESSION_TOKEN
          too, and passing only partial creds causes UnrecognizedClientException.
    """
    kwargs: dict = {"region_name": settings.aws_region}

    # Local mode only: pass explicit endpoint and credentials for DynamoDB Local.
    # In Lambda (no endpoint_url), let boto3 use the IAM role via credential chain.
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        if settings.aws_access_key_id:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
        if settings.aws_secret_access_key:
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    return boto3.resource("dynamodb", **kwargs)


def get_table():
    if using_postgres():
        raise RuntimeError("get_table() is DynamoDB-only; use the database service helpers.")
    db = get_dynamodb_resource()
    return db.Table(settings.dynamodb_table_name)


def get_item(pk: str, sk: str) -> dict | None:
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT data FROM {table_name} WHERE pk = %s AND sk = %s",
                    (pk, sk),
                )
                row = cursor.fetchone()
        return row["data"] if row else None

    table = get_table()
    response = table.get_item(Key={"PK": pk, "SK": sk})
    return response.get("Item")


def query_by_pk(pk: str) -> list[dict]:
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT data FROM {table_name} WHERE pk = %s ORDER BY sk",
                    (pk,),
                )
                return [row["data"] for row in cursor.fetchall()]

    table = get_table()
    response = table.query(KeyConditionExpression=Key("PK").eq(pk))
    return response.get("Items", [])


def query_gsi(gsi_pk_value: str) -> list[dict]:
    """Query GSI1 by GSI1PK — used to fetch all drinks for a cafe."""
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT data
                    FROM {table_name}
                    WHERE gsi1pk = %s
                    ORDER BY gsi1sk
                    """,
                    (gsi_pk_value,),
                )
                return [row["data"] for row in cursor.fetchall()]

    table = get_table()
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(gsi_pk_value),
    )
    return response.get("Items", [])


def scan_by_entity_type(entity_type: str) -> list[dict]:
    """Scan for all items matching an entity type prefix (e.g. SK='METADATA' filtered by PK prefix).
    Not efficient at scale, but fine for a small demo dataset."""
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT data
                    FROM {table_name}
                    WHERE pk LIKE %s AND sk = 'METADATA'
                    ORDER BY pk
                    """,
                    (f"{entity_type}#%",),
                )
                return [row["data"] for row in cursor.fetchall()]

    table = get_table()
    response = table.scan(
        FilterExpression=Attr("PK").begins_with(f"{entity_type}#") & Attr("SK").eq("METADATA"),
    )
    return response.get("Items", [])


def put_item(item: dict) -> None:
    if using_postgres():
        from psycopg.types.json import Jsonb

        normalized = _json_value(item)
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {table_name} (pk, sk, gsi1pk, gsi1sk, data)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (pk, sk) DO UPDATE SET
                        gsi1pk = EXCLUDED.gsi1pk,
                        gsi1sk = EXCLUDED.gsi1sk,
                        data = EXCLUDED.data,
                        updated_at = NOW()
                    """,
                    (
                        normalized["PK"],
                        normalized["SK"],
                        normalized.get("GSI1PK"),
                        normalized.get("GSI1SK"),
                        Jsonb(normalized),
                    ),
                )
        return

    table = get_table()
    table.put_item(Item=item)


def scan_by_sk(sk_value: str) -> list[dict]:
    """Scan for all items with a specific SK value — used to fetch all taste profiles."""
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT data FROM {table_name} WHERE sk = %s ORDER BY pk",
                    (sk_value,),
                )
                return [row["data"] for row in cursor.fetchall()]

    table = get_table()
    response = table.scan(
        FilterExpression=Attr("SK").eq(sk_value),
    )
    return response.get("Items", [])


def get_all_drinks_with_profiles() -> list[dict]:
    """Return a list of dicts each merging a drink METADATA item with its TASTE_PROFILE.
    Drinks without a taste profile are excluded (no data to rank against)."""
    drink_items = scan_by_entity_type("DRINK")
    profile_items = scan_by_sk("TASTE_PROFILE")

    # Index profiles by drink_id for O(1) lookup
    profiles_by_drink_id = {item["drink_id"]: item for item in profile_items}

    result = []
    for drink in drink_items:
        drink_id = drink["drink_id"]
        profile = profiles_by_drink_id.get(drink_id)
        if profile:
            result.append({**drink, "profile": profile})
    return result


def get_all_cafes_by_id() -> dict[str, dict]:
    """Return a dict of cafe_id → cafe metadata item."""
    cafe_items = scan_by_entity_type("CAFE")
    return {item["cafe_id"]: item for item in cafe_items}


def get_cafe_by_external_source(source: str, external_id: str) -> dict | None:
    """Find a cafe by external source/id.

    This scan is acceptable for the local/admin ingestion MVP. At larger scale,
    source + external_id should be indexed with a dedicated GSI.
    """
    if using_postgres():
        table_name = _safe_table_name()
        with _postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT data
                    FROM {table_name}
                    WHERE pk LIKE 'CAFE#%%'
                      AND sk = 'METADATA'
                      AND data->>'source' = %s
                      AND data->>'external_id' = %s
                    LIMIT 1
                    """,
                    (source, external_id),
                )
                row = cursor.fetchone()
        return row["data"] if row else None

    table = get_table()
    response = table.scan(
        FilterExpression=(
            Attr("PK").begins_with("CAFE#")
            & Attr("SK").eq("METADATA")
            & Attr("source").eq(source)
            & Attr("external_id").eq(external_id)
        )
    )
    items = response.get("Items", [])
    return items[0] if items else None


def upsert_cafe_from_external_source(cafe: dict, no_overwrite: bool = False) -> dict:
    """Create/update a cafe metadata item from an external source.

    External metadata is allowed to refresh, but Matcha Scout user-owned records
    such as reviews and drink taste profiles are never touched here.
    """
    existing = get_cafe_by_external_source(cafe["source"], cafe["external_id"])
    item = dict(existing or {})

    user_owned_fields = {"name", "location", "address", "website", "created_at"}
    for key, value in cafe.items():
        if value is None:
            continue
        if no_overwrite and existing and key in user_owned_fields and item.get(key):
            continue
        item[key] = value

    item["PK"] = f"CAFE#{item['cafe_id']}"
    item["SK"] = "METADATA"
    put_item(item)
    return item


def put_external_review_excerpt(cafe_id: str, excerpt: dict) -> None:
    """Store a Yelp review excerpt separately from Matcha Scout user reviews."""
    item = {
        **excerpt,
        "PK": f"CAFE#{cafe_id}",
        "SK": f"EXTERNAL_REVIEW#YELP#{excerpt['external_review_id']}",
        "cafe_id": cafe_id,
    }
    put_item(item)


def list_external_review_excerpts(cafe_id: str) -> list[dict]:
    items = query_by_pk(f"CAFE#{cafe_id}")
    return sorted(
        [item for item in items if item.get("SK", "").startswith("EXTERNAL_REVIEW#")],
        key=lambda item: item.get("time_created") or item.get("ingested_at") or "",
        reverse=True,
    )


def list_reviews_for_drink(drink_id: str) -> list[dict]:
    return sorted(
        [
            item
            for item in query_by_pk(f"DRINK#{drink_id}")
            if item.get("SK", "").startswith("REVIEW#")
        ],
        key=lambda item: item.get("submitted_at", ""),
    )


# ── Manual curation helpers ───────────────────────────────────────────────────

def find_cafe_by_external_id(source: str, external_id: str) -> dict | None:
    """Alias for get_cafe_by_external_source — used by manual curation script."""
    return get_cafe_by_external_source(source, external_id)


def find_existing_drink_for_cafe(cafe_id: str, drink_name: str) -> dict | None:
    """Return the first drink under a cafe whose name matches (case-insensitive).

    Uses a GSI query + in-memory filter. A secondary GSI on drink name would be
    more efficient at scale, but is unnecessary for the admin-curation workflow.
    """
    items = query_gsi(gsi_pk_value=f"CAFE#{cafe_id}")
    name_lower = drink_name.strip().lower()
    for item in items:
        if item.get("SK") == "METADATA" and item.get("name", "").lower() == name_lower:
            return item
    return None


def create_admin_curated_drink(cafe_id: str, drink: dict) -> dict:
    """Persist an admin-curated drink and initialize its neutral taste profile.

    The caller is responsible for setting source, verification_status, and all
    required fields. This helper only writes the two DynamoDB items and returns
    the stored drink item.
    """
    from decimal import Decimal

    drink_id = drink["drink_id"]

    drink_item = {
        **drink,
        "PK": f"DRINK#{drink_id}",
        "SK": "METADATA",
        "GSI1PK": f"CAFE#{cafe_id}",
        "GSI1SK": f"DRINK#{drink_id}",
    }
    put_item(drink_item)

    # Neutral taste profile — review_count 0 means "unrated" confidence.
    # Real taste data only comes from Matcha Scout user reviews.
    put_item({
        "PK": f"DRINK#{drink_id}",
        "SK": "TASTE_PROFILE",
        "drink_id": drink_id,
        "matcha_strength": Decimal("3.0"),
        "sweetness": Decimal("3.0"),
        "creaminess": Decimal("3.0"),
        "earthiness": Decimal("3.0"),
        "bitterness": Decimal("3.0"),
        "review_count": 0,
        "last_updated": drink.get("created_at", ""),
    })

    return drink_item
