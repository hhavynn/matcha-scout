import os


class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    dynamodb_endpoint_url: str = os.getenv("DYNAMODB_ENDPOINT_URL", "http://dynamodb-local:8000")
    dynamodb_table_name: str = os.getenv("DYNAMODB_TABLE_NAME", "matcha_scout")
    # AWS credentials for local DynamoDB (values don't matter, but boto3 requires them)
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "local")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "local")


settings = Settings()
