"""
RAG Lab Backend - FastAPI Application

Main entry point for the RAG Lab API server.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.persistence_routes import router as db_router
from api.comparison_routes import router as comparison_router
from api.analytics_routes import router as analytics_router
from config import settings
from db import init_db, check_database_health
from core.llm import get_api_key_stats
from core.api_keys import initialize_rotator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print(f"Starting RAG Lab Backend v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")

    # Initialize API Key Rotator
    print("Initializing API Key Rotator...")
    rotator = initialize_rotator(
        primary_key=settings.GOOGLE_API_KEY,
        additional_keys=settings.GOOGLE_API_KEYS,
    )
    print(f"API Keys loaded: {rotator.total_keys}")

    # Initialize database
    print("Initializing database...")
    init_db()

    # Check database health
    health = check_database_health()
    print(f"Database status: {health.get('status')}")
    print(f"Database location: {health.get('database')}")
    print(f"Tables: {health.get('table_names')}")

    yield
    # Shutdown
    print("Shutting down RAG Lab Backend")


app = FastAPI(
    title="RAG Lab API",
    description="Backend API for testing 9 RAG techniques with Google Gemini",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Use list instead of string
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Private Network Access headers (Chrome security policy)
@app.middleware("http")
async def add_private_network_headers(request, call_next):
    """Add headers required for Private Network Access (PNA)."""
    response = await call_next(request)

    # Allow requests from public network to private network (localhost)
    response.headers["Access-Control-Allow-Private-Network"] = "true"

    return response

# Include routers
app.include_router(router, prefix="/api/v1", tags=["rag"])
app.include_router(db_router, prefix="/api/v1", tags=["database"])
app.include_router(comparison_router, prefix="/api/v1", tags=["comparison"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Service status
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/api-keys/stats")
async def api_key_stats() -> dict:
    """
    Get API key rotation statistics.

    Returns:
        dict: API key usage stats (keys are masked for security)
    """
    stats = get_api_key_stats()
    # Mask API keys for security
    for key_info in stats.get("keys", []):
        key_info["key_preview"] = "***masked***"
    return stats


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {
        "message": "RAG Lab API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
