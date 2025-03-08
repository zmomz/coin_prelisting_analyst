import os
from typing import List
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "coin prelisting analyst"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_TOKEN: str
    TWITTER_BEARER_TOKEN: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str

    SLACK_WEBHOOK_URL: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
