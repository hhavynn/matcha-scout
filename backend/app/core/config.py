import os


class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    dynamodb_endpoint_url: str = os.getenv("DYNAMODB_ENDPOINT_URL", "http://dynamodb-local:8000")
    dynamodb_table_name: str = os.getenv("DYNAMODB_TABLE_NAME", "matcha_scout")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "local")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "local")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini")
    use_mock_ai: bool = os.getenv("USE_MOCK_AI", "false").lower() == "true"


settings = Settings()
