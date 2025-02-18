from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    
    # Connection settings
    DB_HOST: str = Field(default="localhost", env="SUPABASE_DB_HOST")
    DB_PORT: int = Field(default=5432, env="SUPABASE_DB_PORT")
    DB_NAME: str = Field(default="postgres", env="SUPABASE_DB_NAME")
    DB_USER: str = Field(default="postgres", env="SUPABASE_DB_USER")
    DB_PASSWORD: str = Field(default="postgres", env="SUPABASE_DB_PASSWORD")
    
    # Connection pool settings
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # SSL settings
    DB_SSL_MODE: str = Field(default="require", env="DB_SSL_MODE")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSL_MODE}"


# Create database settings instance
db_settings = DatabaseSettings() 