"""
Configuration module for the application.

This module provides a centralized configuration system using Pydantic settings.
Settings are loaded from environment variables and .env files, with proper type validation
and documentation.

Usage:
    from src.config import settings
    
    # Access settings
    db_url = settings.database.get_sqlalchemy_url()
    api_host = settings.api.HOST
    storage_path = settings.storage.storage_dir
"""

from src.api.config.settings import settings

__all__ = ["settings"] 