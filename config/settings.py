from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    VIDEO_DIR: Path = STORAGE_DIR / "videos"
    AUDIO_DIR: Path = STORAGE_DIR / "audio"

    # Database
    DATABASE_URL: Optional[str] = None
    SUPABASE_DB_USER: str = "postgres"
    SUPABASE_DB_PASSWORD: Optional[str] = None
    SUPABASE_DB_HOST: Optional[str] = None
    SUPABASE_DB_PORT: int = 5432
    SUPABASE_DB_NAME: str = "postgres"

    # External services
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

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
        """Construct SQLAlchemy URL with SSL mode."""
        if self.DATABASE_URL:
            # If DATABASE_URL is provided, append sslmode if not present
            if "sslmode=" not in self.DATABASE_URL:
                return f"{self.DATABASE_URL}?sslmode=require"
            return self.DATABASE_URL
            
        # Construct URL from individual components
        return (
            f"postgresql://{self.SUPABASE_DB_USER}:{self.SUPABASE_DB_PASSWORD}"
            f"@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}"
            "?sslmode=require"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()

# Create necessary directories
settings.STORAGE_DIR.mkdir(exist_ok=True)
settings.VIDEO_DIR.mkdir(exist_ok=True)
settings.AUDIO_DIR.mkdir(exist_ok=True) 