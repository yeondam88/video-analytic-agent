from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse, quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
import logging
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)


class ServiceSettings(BaseSettings):
    """Settings for external services."""
    DEEPGRAM_API_KEY: str = Field(default=os.getenv("DEEPGRAM_API_KEY", ""))
    DEEPGRAM_MODEL: str = "nova-2"  # Using nova-2 model which has good support for Korean
    DEEPGRAM_LANGUAGE: str = "ko"   # Set Korean as default language
    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    
    model_config = {
        "env_prefix": ""
    }


class MeilisearchSettings(BaseSettings):
    """Meilisearch configuration settings."""
    host: str = Field(default=os.getenv("MEILISEARCH__HOST", "http://localhost:7700"))
    api_key: str = Field(default=os.getenv("MEILISEARCH__API_KEY", ""))
    video_index: str = "videos"
    segment_index: str = "segments"
    embeddings_index: str = "embeddings"
    max_total_hits: int = 100
    search_limit: int = 20
    
    model_config = {
        "env_prefix": ""
    }


class Settings(BaseSettings):
    # Base directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    STORAGE_DIR: Path = Field(default=Path(os.getenv("STORAGE_DIR", "./storage")))
    VIDEO_DIR: Path = Field(default=Path(os.getenv("VIDEO_DIR", "./storage/videos")))
    AUDIO_DIR: Path = Field(default=Path(os.getenv("AUDIO_DIR", "./storage/audio")))

    # Database
    DATABASE_URL: Optional[str] = Field(default=os.getenv("DATABASE_URL", None))
    SUPABASE_DB_USER: str = Field(default=os.getenv("SUPABASE_DB_USER", "postgres"))
    SUPABASE_DB_PASSWORD: Optional[str] = Field(default=os.getenv("SUPABASE_DB_PASSWORD", None))
    SUPABASE_DB_HOST: Optional[str] = Field(default=os.getenv("SUPABASE_DB_HOST", None))
    SUPABASE_DB_PORT: int = Field(default=int(os.getenv("SUPABASE_DB_PORT", "5432")))
    SUPABASE_DB_NAME: str = Field(default=os.getenv("SUPABASE_DB_NAME", "postgres"))
    DB_POOL_SIZE: int = 5
    DB_POOL_TIMEOUT: int = 30

    # External services configuration
    services: ServiceSettings = ServiceSettings()

    # API settings
    API_HOST: str = Field(default=os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = Field(default=int(os.getenv("API_PORT", "8000")))

    # Meilisearch configuration
    meilisearch: MeilisearchSettings = MeilisearchSettings()
    
    model_config = {
        "env_prefix": ""
    }

    @model_validator(mode='after')
    def set_db_credentials_from_url(self) -> 'Settings':
        """Extract database credentials from DATABASE_URL if provided."""
        if self.DATABASE_URL:
            parsed = urlparse(self.DATABASE_URL)
            if parsed.hostname:
                self.SUPABASE_DB_HOST = parsed.hostname
            if parsed.password:
                self.SUPABASE_DB_PASSWORD = parsed.password
            if parsed.username:
                self.SUPABASE_DB_USER = parsed.username
            if parsed.port:
                self.SUPABASE_DB_PORT = parsed.port
            if parsed.path[1:]:  # Remove leading slash
                self.SUPABASE_DB_NAME = parsed.path[1:]
        return self

    def get_sqlalchemy_url(self) -> str:
        """Get SQLAlchemy URL with connection pool settings."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Construct URL from individual settings
        password = quote_plus(self.SUPABASE_DB_PASSWORD) if self.SUPABASE_DB_PASSWORD else ""
        url = f"postgresql://{self.SUPABASE_DB_USER}:{password}@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}"
        
        # Add SSL mode for non-local connections
        if self.SUPABASE_DB_HOST not in ('localhost', '127.0.0.1'):
            url += "?sslmode=require"
        
        logger.info(f"Current database settings:")
        logger.info(f"Host: {self.SUPABASE_DB_HOST}")
        logger.info(f"Port: {self.SUPABASE_DB_PORT}")
        logger.info(f"Database: {self.SUPABASE_DB_NAME}")
        logger.info(f"User: {self.SUPABASE_DB_USER}")
        logger.info(f"Constructed database URL: {url.replace(password, '***')}")
        
        return url

settings = Settings()