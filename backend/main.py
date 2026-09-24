"""
AgriNova AI — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers

# Import all models so Base.metadata sees them
import app.models  # noqa: F401

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.farms import router as farms_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.crops import router as crops_router
from app.api.v1.weather import router as weather_router
from app.api.v1.fertilizer import router as fertilizer_router
from app.api.v1.irrigation import router as irrigation_router
from app.api.v1.disease import router as disease_router
from app.api.v1.market import router as market_router

# V2.0 routers
from app.api.v1.analytics import router as analytics_router
from app.api.v1.activity import router as activity_router
from app.api.v1.scheduler import router as scheduler_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.preferences import router as preferences_router
from app.api.v1.reports import router as reports_router

# V3.0 routers
from app.api.v1.ai import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup: create tables (dev mode with SQLite)
    if settings.is_sqlite:
        await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Precision Agriculture Platform — from seed to harvest.",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
def get_cors_origins() -> list[str]:
    return [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ──
register_exception_handlers(app)

# ── Routers ──
app.include_router(auth_router, prefix="/api/v1")
app.include_router(farms_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(crops_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(fertilizer_router, prefix="/api/v1")
app.include_router(irrigation_router, prefix="/api/v1")
app.include_router(disease_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")

# V2.0 routers
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(activity_router, prefix="/api/v1")
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")

# V3.0 routers
app.include_router(ai_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check():
    """API health check endpoint."""
    return {
        "status": "success",
        "message": f"{settings.APP_NAME} API is running",
        "version": "3.0.0",
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health():
    """API v1 health check."""
    return {"status": "success", "message": "API v1 is healthy"}


if __name__ == "__main__":
    import uvicorn
    should_reload = settings.DEBUG and settings.APP_ENV == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=should_reload)
