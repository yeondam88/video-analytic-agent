"""Path settings for the application."""
from pathlib import Path
from typing import Optional
from pydantic import Field, model_validator
from loguru import logger

from .base import BaseAppSettings

class PathSettings(BaseAppSettings):
    """Settings for file system paths."""
    
    # Base directories
    BASE_DIR: Path = Field(
        default=Path(__file__).parent.parent.parent.parent.parent,
        description="Root directory of the project"
    )
    STORAGE_DIR: Path = Field(
        default=None,
        description="Directory for storing uploaded files"
    )
    VIDEO_DIR: Path = Field(
        default=None,
        description="Directory for storing video files"
    )
    AUDIO_DIR: Path = Field(
        default=None,
        description="Directory for storing audio files"
    )
    
    @model_validator(mode='after')
    def ensure_paths(self) -> 'PathSettings':
        """Ensure all paths exist and are properly set."""
        try:
            # Set default paths if not provided
            if self.STORAGE_DIR is None:
                self.STORAGE_DIR = self.BASE_DIR / "storage"
            if self.VIDEO_DIR is None:
                self.VIDEO_DIR = self.STORAGE_DIR / "videos"
            if self.AUDIO_DIR is None:
                self.AUDIO_DIR = self.STORAGE_DIR / "audio"
            
            # Ensure directories exist
            self.STORAGE_DIR.mkdir(exist_ok=True)
            self.VIDEO_DIR.mkdir(exist_ok=True)
            self.AUDIO_DIR.mkdir(exist_ok=True)
            
            logger.info(f"Storage paths initialized:")
            logger.info(f"Base directory: {self.BASE_DIR}")
            logger.info(f"Storage directory: {self.STORAGE_DIR}")
            logger.info(f"Video directory: {self.VIDEO_DIR}")
            logger.info(f"Audio directory: {self.AUDIO_DIR}")
            
            return self
            
        except Exception as e:
            logger.error(f"Error ensuring paths: {e}")
            raise ValueError(f"Failed to ensure paths: {e}") 