import os
from typing import Optional


class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # DynamoDB endpoint:
    #   Local dev  → set DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000 in .env
    #   AWS Lambda → leave DYNAMODB_ENDPOINT_URL unset; boto3 uses the real AWS endpoint
    dynamodb_endpoint_url: Optional[str] = os.getenv("DYNAMODB_ENDPOINT_URL") or None

    dynamodb_table_name: str = os.getenv("DYNAMODB_TABLE_NAME", "matcha_scout")

    # Explicit credentials:
    #   Local dev  → set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY to any non-empty value
    #   AWS Lambda → leave unset; boto3 discovers IAM role credentials automatically
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID") or None
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY") or None

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini")
    use_mock_ai: bool = os.getenv("USE_MOCK_AI", "false").lower() == "true"

    # CORS allowed origins — comma-separated list.
    #   Local dev  → defaults to localhost:3000
    #   AWS Lambda → set CORS_ALLOWED_ORIGINS to include the Vercel production URL
    cors_allowed_origins_raw: str = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins_raw.split(",") if o.strip()]


settings = Settings()
