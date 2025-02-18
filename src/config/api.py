from typing import List
from pydantic import Field, validator, ConfigDict
from pydantic_settings import BaseSettings
import json

class APISettings(BaseSettings):
    """API server settings."""
    
    model_config = ConfigDict(
        extra='allow',  # Allow extra fields
        env_file=".env",  # Read from .env file
        case_sensitive=True,  # Case sensitive environment variables
        env_prefix="",  # No prefix for environment variables
        env_file_encoding="utf-8",  # Ensure proper encoding
        validate_assignment=True  # Validate values on assignment
    )
    
    # Environment
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT", description="Runtime environment")
    DEBUG: bool = Field(False, env="API_DEBUG", description="Enable debug mode")
    
    # Supabase settings
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL", description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY", description="Supabase project API key")
    SUPABASE_JWT_SECRET: str = Field(..., env="SUPABASE_JWT_SECRET", description="Supabase JWT secret")
    
    # Server settings
    HOST: str = Field("0.0.0.0", env="API_HOST", description="API server host")
    PORT: int = Field(8000, env="API_PORT", description="API server port")
    WORKERS: int = Field(1, env="API_WORKERS", description="Number of worker processes")
    TIMEOUT: int = Field(30, env="API_TIMEOUT", description="Request timeout in seconds")
    
    # CORS settings
    CORS_ORIGINS: str = Field("*", env="CORS_ORIGINS", description="Allowed CORS origins (comma-separated)")
    
    # API metadata
    TITLE: str = "Video Analytics API"
    DESCRIPTION: str = """
    API for processing and analyzing video content with AI.
    Features include:
    - Video transcription
    - Speaker diarization
    - Content summarization
    - Semantic search
    """
    VERSION: str = "1.0.0"
    PREFIX: str = "/api/v1"
    
    # OpenAPI endpoints
    OPENAPI_URL: str = f"{PREFIX}/openapi.json"
    DOCS_URL: str = f"{PREFIX}/docs"
    REDOC_URL: str = f"{PREFIX}/redoc"
    
    # Rate limiting
    RATE_LIMIT_TOKENS_PER_SECOND: float = Field(10.0, env="RATE_LIMIT_TPS")
    RATE_LIMIT_BUCKET_SIZE: int = Field(100, env="RATE_LIMIT_BUCKET")
    
    # Circuit breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(5, env="CB_FAILURE_THRESHOLD")
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: float = Field(60.0, env="CB_RECOVERY_TIMEOUT")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(10, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(100, env="MAX_PAGE_SIZE")
    
    # Cache
    CACHE_TTL_SECONDS: int = Field(300, env="CACHE_TTL", description="Cache TTL in seconds")
    MAX_CACHE_SIZE: int = Field(1000, env="MAX_CACHE_SIZE", description="Maximum cache entries")

    @property
    def cors_origin_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()] 