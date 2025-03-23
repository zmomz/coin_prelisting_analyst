from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = Field("Coin Listing API", env="PROJECT_NAME")
    API_V1_STR: str = Field("/api/v1", env="API_V1_STR")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # DB & Redis
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    TEST_DATABASE_URL: str = Field(..., env="TEST_DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")

    # External APIs
    COINGECKO_API_URL: str = Field("https://api.coingecko.com/api/v3", env="COINGECKO_API_URL")
    GITHUB_API_URL: str = Field("https://api.github.com", env="GITHUB_API_URL")
    GITHUB_TOKEN: Optional[str] = Field(None, env="GITHUB_TOKEN")
    TWITTER_BEARER_TOKEN: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    REDDIT_CLIENT_ID: Optional[str] = Field(None, env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = Field(None, env="REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: Optional[str] = Field(None, env="REDDIT_USER_AGENT")

    # Notifications
    SLACK_WEBHOOK_URL: Optional[str] = Field(None, env="SLACK_WEBHOOK_URL")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list, env="BACKEND_CORS_ORIGINS")

    # Environment
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow"
    }

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


settings = Settings()
