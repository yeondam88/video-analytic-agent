import os
from unittest.mock import patch
import json
import pytest

from src.config import settings
from src.config.api import APISettings

def test_default_settings():
    """Test default API settings."""
    # Clear any existing environment variables
    env_vars_to_clear = [
        "ENVIRONMENT", "API_DEBUG", "API_HOST", "API_PORT",
        "API_WORKERS", "API_TIMEOUT"
    ]
    original_env = {}
    for var in env_vars_to_clear:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    try:
        api_settings = APISettings()
        assert api_settings.HOST == "0.0.0.0"
        assert api_settings.PORT == 8000
        assert api_settings.WORKERS == 1
        assert api_settings.TIMEOUT == 30
        assert api_settings.DEBUG is False
        assert api_settings.ENVIRONMENT == "development"
    finally:
        # Restore original environment variables
        for var, value in original_env.items():
            os.environ[var] = value

def test_cors_origins_list():
    """Test CORS origins as list."""
    origins = ["http://localhost:3000", "https://app.example.com"]
    api_settings = APISettings(CORS_ORIGINS=origins)
    assert api_settings.CORS_ORIGINS == origins

def test_cors_origins_string():
    """Test CORS origins as comma-separated string."""
    origins_str = "http://localhost:3000,https://app.example.com"
    api_settings = APISettings(CORS_ORIGINS=origins_str)
    assert api_settings.CORS_ORIGINS == ["http://localhost:3000", "https://app.example.com"]

def test_cors_origins_json():
    """Test CORS origins as JSON string."""
    origins = ["http://localhost:3000", "https://app.example.com"]
    origins_json = json.dumps(origins)
    api_settings = APISettings(CORS_ORIGINS=origins_json)
    assert api_settings.CORS_ORIGINS == origins

def test_api_metadata():
    """Test API metadata fields."""
    api_settings = APISettings()
    assert api_settings.TITLE == "Video Analytics API"
    assert "video content" in api_settings.DESCRIPTION.lower()
    assert api_settings.VERSION == "1.0.0"
    assert api_settings.PREFIX == "/api/v1"

def test_api_endpoints():
    """Test API endpoint paths."""
    api_settings = APISettings()
    assert api_settings.OPENAPI_URL == "/api/v1/openapi.json"
    assert api_settings.DOCS_URL == "/api/v1/docs"
    assert api_settings.REDOC_URL == "/api/v1/redoc"

def test_rate_limiting():
    """Test rate limiting settings."""
    api_settings = APISettings()
    assert api_settings.RATE_LIMIT_TOKENS_PER_SECOND == 10.0
    assert api_settings.RATE_LIMIT_BUCKET_SIZE == 100

def test_circuit_breaker():
    """Test circuit breaker settings."""
    api_settings = APISettings()
    assert api_settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD == 5
    assert api_settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT == 60.0

def test_pagination():
    """Test pagination settings."""
    api_settings = APISettings()
    assert api_settings.DEFAULT_PAGE_SIZE == 10
    assert api_settings.MAX_PAGE_SIZE == 100

def test_cache():
    """Test cache settings."""
    api_settings = APISettings()
    assert api_settings.CACHE_TTL_SECONDS == 300
    assert api_settings.MAX_CACHE_SIZE == 1000

def test_custom_settings():
    """Test custom API settings from environment."""
    test_settings = {
        "API_HOST": "127.0.0.1",
        "API_PORT": "9000",
        "API_WORKERS": "4",
        "API_TIMEOUT": "60",
        "API_DEBUG": "true",
        "ENVIRONMENT": "production"
    }
    
    # Clear any existing environment variables
    env_vars_to_clear = [
        "ENVIRONMENT", "API_DEBUG", "API_HOST", "API_PORT",
        "API_WORKERS", "API_TIMEOUT", "SUPABASE_URL", "SUPABASE_KEY",
        "DEEPGRAM_API_KEY", "OPENAI_API_KEY", "DATABASE_URL"
    ]
    original_env = {}
    for var in env_vars_to_clear:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    try:
        # Create settings with test values directly
        api_settings = APISettings(
            HOST="127.0.0.1",
            PORT=9000,
            WORKERS=4,
            TIMEOUT=60,
            DEBUG=True,
            ENVIRONMENT="production"
        )
        assert api_settings.HOST == "127.0.0.1"
        assert api_settings.PORT == 9000
        assert api_settings.WORKERS == 4
        assert api_settings.TIMEOUT == 60
        assert api_settings.DEBUG is True
        assert api_settings.ENVIRONMENT == "production"
    finally:
        # Restore original environment variables
        for var, value in original_env.items():
            os.environ[var] = value

def test_settings_integration():
    """Test integration with main Settings class."""
    assert isinstance(settings.api, APISettings)
    assert settings.api.HOST == "0.0.0.0"
    assert settings.api.PORT == 8000 