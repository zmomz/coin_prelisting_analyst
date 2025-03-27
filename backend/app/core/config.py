from typing import Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    ALEMBIC_MAIN_DB: str
    ALEMBIC_TEST_DB: str
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
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=list)

    # Environment
    ENVIRONMENT: str = Field("development")
    LOG_LEVEL: str = Field("INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: Union[str, list[str]]) -> list[str]:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


settings = Settings()
