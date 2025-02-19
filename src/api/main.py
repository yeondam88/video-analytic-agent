from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.database import get_db
from src.api.routers import api_router
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application."""
    # Startup
    try:
        # Test database connection
        db = next(get_db())
        logger.info("Successfully connected to database")
        yield
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Video Analytics API...")
        # Add any cleanup code here if needed

app = FastAPI(
    title="Video Analytics API",
    description="API for video analytics and search",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router which already includes all sub-routers
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db = next(get_db())
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Video Analytics API"} 