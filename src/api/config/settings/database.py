"""Database settings for the application."""
from typing import Optional
from urllib.parse import urlparse, quote_plus
from pydantic import Field, model_validator
from loguru import logger

from .base import BaseAppSettings

class DatabaseSettings(BaseAppSettings):
    """Settings for database connection."""
    
    # Database URL
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL"
    )
    
    # Individual connection settings
    DB_USER: str = Field(
        default="postgres",
        description="Database user"
    )
    DB_PASSWORD: str = Field(
        default="postgres",
        description="Database password"
    )
    DB_HOST: str = Field(
        default="localhost",
        description="Database host"
    )
    DB_PORT: int = Field(
        default=54322,  # Default Supabase CLI port
        description="Database port"
    )
    DB_NAME: str = Field(
        default="postgres",
        description="Database name"
    )
    
    # Connection pool settings
    DB_POOL_SIZE: int = Field(
        default=5,
        description="Database connection pool size"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Database connection pool timeout"
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum number of connections beyond pool size"
    )
    
    @model_validator(mode='after')
    def set_db_credentials_from_url(self) -> 'DatabaseSettings':
        """Extract database credentials from DATABASE_URL if provided."""
        if self.DATABASE_URL:
            try:
                parsed = urlparse(self.DATABASE_URL)
                if parsed.hostname:
                    self.DB_HOST = parsed.hostname
                if parsed.password:
                    self.DB_PASSWORD = parsed.password
                if parsed.username:
                    self.DB_USER = parsed.username
                if parsed.port:
                    self.DB_PORT = parsed.port
                if parsed.path[1:]:  # Remove leading slash
                    self.DB_NAME = parsed.path[1:]
                logger.info("Successfully parsed DATABASE_URL")
            except Exception as e:
                logger.error(f"Error parsing DATABASE_URL: {e}")
                raise ValueError(f"Failed to parse DATABASE_URL: {e}")
        return self
    
    def get_sqlalchemy_url(self) -> str:
        """Get SQLAlchemy URL with connection pool settings."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
        else:
            # Construct URL from individual settings
            password = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
            url = f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # Add SSL mode for non-local connections
        if self.DB_HOST not in ('localhost', '127.0.0.1'):
            url += "?sslmode=require"
        
        logger.info(f"Current database settings:")
        logger.info(f"Host: {self.DB_HOST}")
        logger.info(f"Port: {self.DB_PORT}")
        logger.info(f"Database: {self.DB_NAME}")
        logger.info(f"User: {self.DB_USER}")
        logger.info(f"Constructed database URL: {url.replace(password, '***')}")
        
        return url 