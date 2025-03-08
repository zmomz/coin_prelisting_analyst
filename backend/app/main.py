from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1 import auth, coins, suggestions, users, metrics
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(coins.router, prefix=settings.API_V1_STR, tags=["coins"])
app.include_router(suggestions.router, prefix=settings.API_V1_STR, tags=["suggestions"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(metrics.router, prefix=settings.API_V1_STR, tags=["metrics"])
