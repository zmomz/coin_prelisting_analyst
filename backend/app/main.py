from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth, coins,
    scores, scoring_weights,
    metrics, suggestions, users
)
from app.core.config import settings
from app.core.logging import logger

from app.api.health import router as health_router


API_PREFIX = settings.API_V1_STR if settings.API_V1_STR.startswith("/") else f"/{settings.API_V1_STR}"
logger.info(f"API running with prefix: {API_PREFIX}")

# OpenAPI tags
tags_metadata = [
        {"name": "auth", "description": "Handles user authentication, login,\
          and session management"},
        {"name": "users", "description": "Manages user accounts, roles, and \
         permissions"},
        {"name": "coins", "description": "Provides cryptocurrency listings and \
          detailed metadata"},
        {"name": "scores", "description": "Stores and retrieves evaluation \
          scores for coins based on predefined criteria"},
        {"name": "scoring_weights", "description": "Defines the weighting of \
          different scoring factors to calculate overall coin ratings"},
        {"name": "suggestions", "description": "Captures and manages analyst \
          recommendations and improvement proposals"},
        {"name": "metrics", "description": "Tracks and reports key \
         performance metrics for cryptocurrencies"},
        {"name": "health", "description": "Provides system health status and \
          service availability checks"},
        {"name": "root", "description": "Serves as the base API endpoint with \
          service information"}
]


# Optional: serve custom Reveal.js if not using CDN


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up the Coin Prelisting API...")
    yield
    logger.info("🛑 Shutting down the Coin Prelisting API...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A backend system for assisting cryptocurrency \
              exchanges in listing new coins.",
        version="1.0.0",
        openapi_url=f"{API_PREFIX}/openapi.json",
        lifespan=lifespan,
        openapi_tags=tags_metadata,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Healthcheck & Root
    @app.get("/api/health", tags=["health"])
    async def health_check():
        logger.info("Health check passed.")
        return {"status": "ok"}


    # Routers
    app.include_router(auth.router, prefix=API_PREFIX, tags=["auth"])
    app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
    app.include_router(coins.router, prefix=API_PREFIX, tags=["coins"])
    app.include_router(scores.router, prefix=API_PREFIX, tags=["scores"])
    app.include_router(
        scoring_weights.router, prefix=API_PREFIX, tags=["scoring_weights"]
    )
    app.include_router(
        suggestions.router, prefix=API_PREFIX, tags=["suggestions"]
    )
    app.include_router(metrics.router, prefix=API_PREFIX, tags=["metrics"])
    app.include_router(health_router)
    return app


app = create_app()
