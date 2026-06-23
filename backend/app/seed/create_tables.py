"""
Creates the configured database storage for Matcha Scout.
Run once before seeding data:
  docker compose exec api python -m app.seed.create_tables
"""
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services import db


def create_table():
    if db.using_postgres():
        db.initialize_database()
        print(
            f"PostgreSQL table '{settings.database_table_name}' created successfully "
            "(or already existed)."
        )
        return

    dynamodb_resource = boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    try:
        table = dynamodb_resource.create_table(
            TableName=settings.dynamodb_table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table '{settings.dynamodb_table_name}' created successfully.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"Table '{settings.dynamodb_table_name}' already exists. Skipping.")
        else:
            raise


if __name__ == "__main__":
    create_table()
