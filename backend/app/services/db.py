import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from app.core.config import settings


def get_dynamodb_resource():
    """
    Build a boto3 DynamoDB resource that works in both environments:

    Local dev (Docker):
        DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
        AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY set to any non-empty value
        → passes explicit endpoint + credentials to reach DynamoDB Local

    AWS Lambda:
        DYNAMODB_ENDPOINT_URL unset (None)
        AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY unset (None)
        → boto3 discovers the real DynamoDB endpoint and uses the Lambda IAM role
    """
    kwargs: dict = {"region_name": settings.aws_region}

    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id

    if settings.aws_secret_access_key:
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    return boto3.resource("dynamodb", **kwargs)


def get_table():
    db = get_dynamodb_resource()
    return db.Table(settings.dynamodb_table_name)


def get_item(pk: str, sk: str) -> dict | None:
    table = get_table()
    response = table.get_item(Key={"PK": pk, "SK": sk})
    return response.get("Item")


def query_by_pk(pk: str) -> list[dict]:
    table = get_table()
    response = table.query(KeyConditionExpression=Key("PK").eq(pk))
    return response.get("Items", [])


def query_gsi(gsi_pk_value: str) -> list[dict]:
    """Query GSI1 by GSI1PK — used to fetch all drinks for a cafe."""
    table = get_table()
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(gsi_pk_value),
    )
    return response.get("Items", [])


def scan_by_entity_type(entity_type: str) -> list[dict]:
    """Scan for all items matching an entity type prefix (e.g. SK='METADATA' filtered by PK prefix).
    Not efficient at scale, but fine for a small demo dataset."""
    table = get_table()
    response = table.scan(
        FilterExpression=Attr("PK").begins_with(f"{entity_type}#") & Attr("SK").eq("METADATA"),
    )
    return response.get("Items", [])


def put_item(item: dict) -> None:
    table = get_table()
    table.put_item(Item=item)


def scan_by_sk(sk_value: str) -> list[dict]:
    """Scan for all items with a specific SK value — used to fetch all taste profiles."""
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
