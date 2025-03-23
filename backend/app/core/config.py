from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = Field("Coin Listing API")
    API_V1_STR: str = Field("/api/v1")
    SECRET_KEY: str

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)

    # DB & Redis
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # External APIs
    COINGECKO_API_URL: str = Field("https://api.coingecko.com/api/v3")
    GITHUB_API_URL: str = Field("https://api.github.com")
    GITHUB_TOKEN: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: Optional[str] = None

    # Notifications
    SLACK_WEBHOOK_URL: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Environment
    ENVIRONMENT: str = Field("development")
    LOG_LEVEL: str = Field("INFO")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
        "env_map": {
            "PROJECT_NAME": "PROJECT_NAME",
            "API_V1_STR": "API_V1_STR",
            "SECRET_KEY": "SECRET_KEY",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "ACCESS_TOKEN_EXPIRE_MINUTES",
            "DATABASE_URL": "DATABASE_URL",
            "TEST_DATABASE_URL": "TEST_DATABASE_URL",
            "REDIS_URL": "REDIS_URL",
            "CELERY_BROKER_URL": "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND": "CELERY_RESULT_BACKEND",
            "COINGECKO_API_URL": "COINGECKO_API_URL",
            "GITHUB_API_URL": "GITHUB_API_URL",
            "GITHUB_TOKEN": "GITHUB_TOKEN",
            "TWITTER_BEARER_TOKEN": "TWITTER_BEARER_TOKEN",
            "REDDIT_CLIENT_ID": "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET": "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT": "REDDIT_USER_AGENT",
            "SLACK_WEBHOOK_URL": "SLACK_WEBHOOK_URL",
            "BACKEND_CORS_ORIGINS": "BACKEND_CORS_ORIGINS",
            "ENVIRONMENT": "ENVIRONMENT",
            "LOG_LEVEL": "LOG_LEVEL"
        }
    }

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


settings = Settings()
