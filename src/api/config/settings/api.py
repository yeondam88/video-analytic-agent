"""API settings for the application."""
from typing import List
from pydantic import Field, model_validator
from loguru import logger

from .base import BaseAppSettings

class APISettings(BaseAppSettings):
    """Settings for the API server."""
    
    # Server settings
    HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server"
    )
    PORT: int = Field(
        default=8000,
        description="Port to bind the API server"
    )
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Whether to allow credentials in CORS requests"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="List of allowed HTTP headers"
    )
    
    # API documentation
    TITLE: str = Field(
        default="Video Analytics API",
        description="Title of the API"
    )
    DESCRIPTION: str = Field(
        default="API for processing and analyzing video content",
        description="Description of the API"
    )
    VERSION: str = Field(
        default="1.0.0",
        description="Version of the API"
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Whether to enable rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Number of requests allowed per window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Time window in seconds for rate limiting"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        """Get list of allowed CORS origins."""
        try:
            if not self.CORS_ORIGINS:
                logger.warning("CORS_ORIGINS is empty, using default values")
                return ["http://localhost:3000", "http://127.0.0.1:5173"]
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            logger.info(f"Configured CORS origins: {origins}")
            return origins
        except Exception as e:
            logger.error(f"Error processing CORS origins: {e}")
            return ["http://localhost:3000", "http://127.0.0.1:5173"]
    
    @model_validator(mode='after')
    def validate_cors_settings(self) -> 'APISettings':
        """Validate CORS settings."""
        try:
            # Ensure CORS_ORIGINS is not empty
            if not self.CORS_ORIGINS:
                self.CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:5173"
                logger.warning("Empty CORS_ORIGINS, using default values")
            
            # Validate that we can parse the origins
            _ = self.cors_origin_list
            logger.info("CORS settings validated successfully")
            return self
        except Exception as e:
            logger.error(f"Error validating CORS settings: {e}")
            raise ValueError(f"Invalid CORS settings: {e}") 