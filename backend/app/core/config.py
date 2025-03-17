from decouple import config
from typing import List
from pydantic import AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = config("PROJECT_NAME")
    API_V1_STR: str = config("API_V1_STR")
    SECRET_KEY: str = config("SECRET_KEY")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES")

    DATABASE_URL: str = config("DATABASE_URL")
    TEST_DATABASE_URL: str = config("TEST_DATABASE_URL")
    REDIS_URL: str = config("REDIS_URL")
    CELERY_BROKER_URL: str = config("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = config("CELERY_RESULT_BACKEND")

    COINGECKO_API_URL: str = config("COINGECKO_API_URL")
    GITHUB_API_URL: str = config("GITHUB_API_URL")
    GITHUB_TOKEN: str = config("GITHUB_TOKEN")
    TWITTER_BEARER_TOKEN: str = config("TWITTER_BEARER_TOKEN")
    REDDIT_CLIENT_ID: str = config("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = config("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = config("REDDIT_USER_AGENT")

    SLACK_WEBHOOK_URL: str = config("SLACK_WEBHOOK_URL")

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = config("BACKEND_CORS_ORIGINS")

    ENVIRONMENT: str = config("ENVIRONMENT")
    LOG_LEVEL: str = config("LOG_LEVEL")

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")


settings = Settings()
