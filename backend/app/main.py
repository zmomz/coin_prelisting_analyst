import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1 import auth, coins, suggestions, users, metrics
from app.core.config import settings

# Ensure API version prefix starts with `/`
API_PREFIX = settings.API_V1_STR if settings.API_V1_STR.startswith("/") else f"/{settings.API_V1_STR}"

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A backend system for assisting cryptocurrency exchanges in listing new coins.",
    version="1.0.0",
    openapi_url=f"{API_PREFIX}/openapi.json"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],  # Allow all origins if not set
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    logger.info("Health check passed.")
    return {"status": "ok"}

# Root endpoint for quick API check
@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the Coin Prelisting API!"}

# Include API routers
app.include_router(auth.router, prefix=API_PREFIX, tags=["auth"])
app.include_router(coins.router, prefix=API_PREFIX, tags=["coins"])
app.include_router(suggestions.router, prefix=API_PREFIX, tags=["suggestions"])
app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
app.include_router(metrics.router, prefix=API_PREFIX, tags=["metrics"])

logger.info(f"API running with prefix: {API_PREFIX}")
