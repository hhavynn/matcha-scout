import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from app.core.config import settings


def get_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


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
