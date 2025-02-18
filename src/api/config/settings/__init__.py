"""Settings initialization and configuration."""
from typing import Optional
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .paths import PathSettings
from .database import DatabaseSettings
from .services import ExternalServicesSettings
from .api import APISettings

class Settings(BaseSettings):
    """Combined settings for the application."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # Nested settings
    paths: PathSettings = Field(default_factory=PathSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    services: ExternalServicesSettings = Field(default_factory=ExternalServicesSettings)
    api: APISettings = Field(default_factory=APISettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    @model_validator(mode='after')
    def initialize_nested_settings(self) -> 'Settings':
        """Initialize nested settings and handle flat environment variables."""
        # Initialize nested settings if not already initialized
        if not isinstance(self.api, APISettings):
            self.api = APISettings()
        if not isinstance(self.database, DatabaseSettings):
            self.database = DatabaseSettings()
        if not isinstance(self.paths, PathSettings):
            self.paths = PathSettings()
        if not isinstance(self.services, ExternalServicesSettings):
            self.services = ExternalServicesSettings()

        # Handle flat environment variables
        import os
        
        # Map flat env vars to nested settings
        env_mapping = {
            'DEEPGRAM_API_KEY': ('services', 'DEEPGRAM_API_KEY'),
            'DEEPGRAM_MODEL': ('services', 'DEEPGRAM_MODEL'),
            'OPENAI_API_KEY': ('services', 'OPENAI_API_KEY'),
            'OPENAI_MODEL': ('services', 'OPENAI_MODEL'),
            'OPENAI_EMBEDDING_MODEL': ('services', 'OPENAI_EMBEDDING_MODEL'),
            'SUPABASE_URL': ('services', 'SUPABASE_URL'),
            'SUPABASE_KEY': ('services', 'SUPABASE_KEY'),
            'VIDEO_DIR': ('paths', 'VIDEO_DIR'),
            'AUDIO_DIR': ('paths', 'AUDIO_DIR'),
            'STORAGE_DIR': ('paths', 'STORAGE_DIR'),
            'BASE_DIR': ('paths', 'BASE_DIR'),
        }

        # Copy values from flat env vars to nested settings
        for env_var, (section, key) in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                nested_settings = getattr(self, section)
                setattr(nested_settings, key, value)

        return self

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Global settings instance
settings = get_settings() 