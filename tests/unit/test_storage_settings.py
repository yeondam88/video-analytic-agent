import os
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

from src.config import settings
from src.config.storage import StorageSettings

def test_default_settings():
    """Test default storage settings."""
    storage_settings = StorageSettings()
    assert storage_settings.MAX_STORAGE_GB == 5.0
    assert storage_settings.CLEANUP_DAYS == 7
    assert isinstance(storage_settings.base_dir, Path)
    assert isinstance(storage_settings.storage_dir, Path)
    assert isinstance(storage_settings.video_dir, Path)
    assert isinstance(storage_settings.audio_dir, Path)

def test_directory_structure():
    """Test directory structure and paths."""
    storage_settings = StorageSettings()
    assert storage_settings.video_dir.parent == storage_settings.storage_dir
    assert storage_settings.audio_dir.parent == storage_settings.storage_dir
    assert "storage" in str(storage_settings.storage_dir)
    assert "videos" in str(storage_settings.video_dir)
    assert "audio" in str(storage_settings.audio_dir)

def test_custom_paths():
    """Test custom storage paths."""
    test_settings = {
        "STORAGE_DIR": "/tmp/test_storage",
        "VIDEO_DIR": "/tmp/test_storage/test_videos",
        "AUDIO_DIR": "/tmp/test_storage/test_audio"
    }
    with patch.dict(os.environ, test_settings):
        storage_settings = StorageSettings()
        assert str(storage_settings.storage_dir) == "/tmp/test_storage"
        assert str(storage_settings.video_dir) == "/tmp/test_storage/test_videos"
        assert str(storage_settings.audio_dir) == "/tmp/test_storage/test_audio"

def test_directory_creation():
    """Test directory creation on initialization."""
    test_dir = Path("/tmp/test_storage_init")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_settings = {
        "STORAGE_DIR": str(test_dir),
        "VIDEO_DIR": str(test_dir / "videos"),
        "AUDIO_DIR": str(test_dir / "audio")
    }
    
    with patch.dict(os.environ, test_settings):
        storage_settings = StorageSettings()
        assert test_dir.exists()
        assert (test_dir / "videos").exists()
        assert (test_dir / "audio").exists()
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

def test_custom_limits():
    """Test custom storage limits."""
    test_settings = {
        "MAX_STORAGE_GB": "10.5",
        "CLEANUP_DAYS": "14"
    }
    with patch.dict(os.environ, test_settings):
        storage_settings = StorageSettings()
        assert storage_settings.MAX_STORAGE_GB == 10.5
        assert storage_settings.CLEANUP_DAYS == 14

def test_path_properties():
    """Test path property getters."""
    storage_settings = StorageSettings()
    assert storage_settings.base_dir == storage_settings._base_dir
    assert storage_settings.storage_dir == storage_settings._storage_dir
    assert storage_settings.video_dir == storage_settings._video_dir
    assert storage_settings.audio_dir == storage_settings._audio_dir

def test_path_validation_error():
    """Test path validation error handling."""
    with patch('pathlib.Path.mkdir', side_effect=PermissionError):
        with pytest.raises(ValueError, match="Failed to ensure paths"):
            StorageSettings()

def test_settings_integration():
    """Test integration with main Settings class."""
    assert isinstance(settings.storage, StorageSettings)
    assert settings.storage.MAX_STORAGE_GB == 5.0
    assert settings.storage.CLEANUP_DAYS == 7
    assert isinstance(settings.storage.storage_dir, Path) 