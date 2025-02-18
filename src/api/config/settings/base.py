"""Base settings for the application."""
from typing import Any, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

class BaseAppSettings(BaseSettings):
    """Base settings class with common functionality."""
    
    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to exclude None values by default."""
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True
    ) 