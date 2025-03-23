from app.core.logging import logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import auth, coins, suggestions, users, metrics
from app.core.config import settings


# API version prefix
API_PREFIX = settings.API_V1_STR if settings.API_V1_STR.startswith("/") else f"/{settings.API_V1_STR}"
logger.info(f"API running with prefix: {API_PREFIX}")

# Optional: OpenAPI tag groups for Swagger
tags_metadata = [
    {"name": "auth", "description": "Authentication and user login"},
    {"name": "users", "description": "User management and roles"},
    {"name": "coins", "description": "Coin listing and metadata"},
    {"name": "suggestions", "description": "Analyst suggestions and proposals"},
    {"name": "metrics", "description": "Coin metrics tracking"},
    {"name": "health", "description": "Healthcheck endpoint"},
    {"name": "root", "description": "Root welcome route"},
]

# FastAPI lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the Coin Prelisting API...")
    yield
    logger.info("Shutting down the Coin Prelisting API...")

# Create app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A backend system for assisting cryptocurrency exchanges in listing new coins.",
    version="1.0.0",
    openapi_url=f"{API_PREFIX}/openapi.json",
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health", tags=["health"])
async def health_check():
    logger.info("Health check passed.")
    return {"status": "ok"}

# Root route
@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the Coin Prelisting API!"}

# Include versioned API routers
app.include_router(auth.router, prefix=API_PREFIX, tags=["auth"])
app.include_router(coins.router, prefix=API_PREFIX, tags=["coins"])
app.include_router(suggestions.router, prefix=API_PREFIX, tags=["suggestions"])
app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
app.include_router(metrics.router, prefix=API_PREFIX, tags=["metrics"])
