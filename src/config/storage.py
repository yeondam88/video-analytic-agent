from pathlib import Path
from pydantic import Field, model_validator, ConfigDict
from pydantic_settings import BaseSettings
from loguru import logger

class StorageSettings(BaseSettings):
    """Storage settings for file management."""
    
    model_config = ConfigDict(
        extra='allow',  # Allow extra fields
        env_file=None,  # Don't read from .env file in tests
        case_sensitive=True,  # Case sensitive environment variables
        env_prefix="",  # No prefix for environment variables
        env_file_encoding="utf-8"  # Ensure proper encoding
    )
    
    # Base directories
    BASE_DIR: str = Field(
        default=str(Path(__file__).parent.parent.parent),
        description="Root directory of the project"
    )
    STORAGE_DIR: str = Field(
        default=str(Path(__file__).parent.parent.parent / "storage"),
        description="Directory for storing uploaded files"
    )
    VIDEO_DIR: str = Field(
        default=str(Path(__file__).parent.parent.parent / "storage" / "videos"),
        description="Directory for storing video files"
    )
    AUDIO_DIR: str = Field(
        default=str(Path(__file__).parent.parent.parent / "storage" / "audio"),
        description="Directory for storing audio files"
    )
    
    # Storage limits
    MAX_STORAGE_GB: float = Field(5.0, env="MAX_STORAGE_GB", description="Maximum storage size in GB")
    CLEANUP_DAYS: int = Field(7, env="CLEANUP_DAYS", description="Days to keep files before cleanup")
    
    # Internal state
    _base_dir: Path | None = None
    _storage_dir: Path | None = None
    _video_dir: Path | None = None
    _audio_dir: Path | None = None

    @model_validator(mode='after')
    def ensure_paths(self) -> 'StorageSettings':
        """Convert string paths to Path objects and ensure they exist."""
        try:
            # Convert string paths to Path objects
            self._base_dir = Path(self.BASE_DIR)
            
            # Set default paths if not provided
            if not self.STORAGE_DIR:
                self.STORAGE_DIR = str(self._base_dir / "storage")
            if not self.VIDEO_DIR:
                self.VIDEO_DIR = str(Path(self.STORAGE_DIR) / "videos")
            if not self.AUDIO_DIR:
                self.AUDIO_DIR = str(Path(self.STORAGE_DIR) / "audio")
            
            # Convert to Path objects
            self._storage_dir = Path(self.STORAGE_DIR)
            self._video_dir = Path(self.VIDEO_DIR)
            self._audio_dir = Path(self.AUDIO_DIR)

            # Create directories if they don't exist
            self._storage_dir.mkdir(exist_ok=True)
            self._video_dir.mkdir(exist_ok=True)
            self._audio_dir.mkdir(exist_ok=True)

            logger.info("Successfully created storage directories")
            return self
        except Exception as e:
            logger.error(f"Error ensuring paths: {e}")
            raise ValueError(f"Failed to ensure paths: {e}")

    @property
    def base_dir(self) -> Path:
        """Get the base directory path."""
        return self._base_dir

    @property
    def storage_dir(self) -> Path:
        """Get the storage directory path."""
        return self._storage_dir

    @property
    def video_dir(self) -> Path:
        """Get the video directory path."""
        return self._video_dir

    @property
    def audio_dir(self) -> Path:
        """Get the audio directory path."""
        return self._audio_dir 