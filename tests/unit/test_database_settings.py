import os
from unittest.mock import patch
import pytest
from urllib.parse import quote_plus

from src.config import settings
from src.config.database import DatabaseSettings

def test_default_settings():
    """Test default database settings."""
    db_settings = DatabaseSettings()
    assert db_settings.DB_HOST == "localhost"
    assert db_settings.DB_PORT == 5432
    assert db_settings.DB_USER == "postgres"
    assert db_settings.DB_PASSWORD == "postgres"
    assert db_settings.DB_NAME == "video_analytics"
    assert db_settings.DB_POOL_SIZE == 5
    assert db_settings.DB_POOL_TIMEOUT == 30

def test_database_url_construction():
    """Test database URL construction."""
    db_settings = DatabaseSettings()
    expected_url = f"postgresql://postgres:{quote_plus('postgres')}@localhost:5432/video_analytics"
    assert db_settings.DATABASE_URL == expected_url

def test_custom_settings():
    """Test custom database settings."""
    test_settings = {
        "DB_HOST": "testhost",
        "DB_PORT": 5433,
        "DB_USER": "testuser",
        "DB_PASSWORD": "test@pass",
        "DB_NAME": "testdb",
        "DB_POOL_SIZE": 10,
        "DB_POOL_TIMEOUT": 60
    }
    db_settings = DatabaseSettings(**test_settings)
    expected_url = f"postgresql://testuser:{quote_plus('test@pass')}@testhost:5433/testdb"
    assert db_settings.DATABASE_URL == expected_url

def test_direct_database_url():
    """Test direct DATABASE_URL setting."""
    direct_url = "postgresql://user:pass@host:5432/db"
    db_settings = DatabaseSettings(DATABASE_URL=direct_url)
    assert db_settings.DATABASE_URL == direct_url

def test_sqlalchemy_url():
    """Test SQLAlchemy URL construction."""
    db_settings = DatabaseSettings()
    expected_url = f"postgresql://postgres:{quote_plus('postgres')}@localhost:5432/video_analytics?pool_size=5&pool_timeout=30"
    assert db_settings.get_sqlalchemy_url() == expected_url

def test_settings_integration():
    """Test integration with main Settings class."""
    test_env = {
        "DB_HOST": "testhost",
        "DB_PORT": "5433",
        "DB_USER": "testuser",
        "DB_PASSWORD": "test@pass",
        "DB_NAME": "testdb",
        "DB_POOL_SIZE": "10",
        "DB_POOL_TIMEOUT": "60",
        "DATABASE_URL": ""  # Empty string instead of None
    }
    
    # Clear any existing environment variables
    env_vars_to_clear = [
        "SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_DB_HOST", "SUPABASE_DB_USER",
        "SUPABASE_DB_PASSWORD", "SUPABASE_DB_NAME", "SUPABASE_DB_PORT",
        "DATABASE_URL"
    ]
    original_env = {}
    for var in env_vars_to_clear:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    try:
        with patch.dict(os.environ, test_env, clear=True):
            # Create new settings instance to pick up test environment
            from src.config import get_settings
            test_settings = get_settings()
            
            # Check that environment variables are properly passed through
            assert test_settings.DB_HOST == "testhost"
            assert test_settings.DB_PORT == 5433
            assert test_settings.DB_USER == "testuser"
            assert test_settings.DB_PASSWORD == "test@pass"
            assert test_settings.DB_NAME == "testdb"
            assert test_settings.DB_POOL_SIZE == 10
            assert test_settings.DB_POOL_TIMEOUT == 60
            
            # Check that DatabaseSettings is properly constructed
            db = test_settings.database
            assert db.DB_HOST == "testhost"
            assert db.DB_PORT == 5433
            assert db.DB_USER == "testuser"
            assert db.DB_PASSWORD == "test@pass"
            assert db.DB_NAME == "testdb"
            assert db.DB_POOL_SIZE == 10
            assert db.DB_POOL_TIMEOUT == 60
            
            # Verify URL construction
            expected_url = f"postgresql://testuser:{quote_plus('test@pass')}@testhost:5433/testdb"
            assert db.DATABASE_URL == expected_url
    finally:
        # Restore original environment variables
        for var, value in original_env.items():
            os.environ[var] = value

def test_password_encoding():
    """Test password encoding in database URL."""
    db_settings = DatabaseSettings(DB_PASSWORD="pass@word!123")
    assert quote_plus("pass@word!123") in db_settings.DATABASE_URL 