import os
import time
import shutil
from pathlib import Path
from loguru import logger
from typing import List, Optional

from config.settings import settings

class StorageCleanupService:
    """Service for managing storage cleanup of temporary files."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or settings.STORAGE_PATH)
        self.storage_dirs = ["videos", "audio"]
        
    def initialize_storage(self):
        """Initialize storage directories if they don't exist."""
        for dir_name in self.storage_dirs:
            dir_path = self.storage_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized storage directory: {dir_path}")
    
    def cleanup_old_files(self, max_age_days: int = 7) -> List[Path]:
        """Remove files older than max_age_days."""
        removed_files = []
        cutoff_time = time.time() - (max_age_days * 86400)
        
        for dir_name in self.storage_dirs:
            dir_path = self.storage_path / dir_name
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.glob("**/*"):
                try:
                    if not file_path.is_file():
                        continue
                        
                    mtime = file_path.stat().st_mtime
                    if mtime < cutoff_time:
                        file_path.unlink()
                        removed_files.append(file_path)
                        logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
        
        return removed_files
    
    def cleanup_by_pattern(self, pattern: str) -> List[Path]:
        """Remove files matching a specific pattern."""
        removed_files = []
        
        for dir_name in self.storage_dirs:
            dir_path = self.storage_path / dir_name
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_files.append(file_path)
                        logger.info(f"Removed file matching pattern {pattern}: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")
        
        return removed_files
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics for each directory."""
        stats = {}
        
        for dir_name in self.storage_dirs:
            dir_path = self.storage_path / dir_name
            if not dir_path.exists():
                stats[dir_name] = {"size": 0, "count": 0}
                continue
            
            total_size = 0
            file_count = 0
            
            for file_path in dir_path.glob("**/*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            stats[dir_name] = {
                "size": total_size,
                "count": file_count
            }
        
        return stats
    
    def ensure_space_available(self, required_bytes: int, buffer_factor: float = 1.5) -> bool:
        """Ensure enough space is available, removing old files if necessary."""
        total_required = int(required_bytes * buffer_factor)
        
        # Get current free space
        free_space = shutil.disk_usage(self.storage_path).free
        if free_space >= total_required:
            return True
            
        # Try to free up space by removing old files
        needed_space = total_required - free_space
        logger.warning(f"Need to free up {needed_space} bytes")
        
        # Remove files starting with the oldest until we have enough space
        files_by_age = []
        for dir_name in self.storage_dirs:
            dir_path = self.storage_path / dir_name
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.glob("**/*"):
                if file_path.is_file():
                    files_by_age.append((file_path, file_path.stat().st_mtime))
        
        # Sort by modification time (oldest first)
        files_by_age.sort(key=lambda x: x[1])
        
        freed_space = 0
        for file_path, _ in files_by_age:
            try:
                size = file_path.stat().st_size
                file_path.unlink()
                freed_space += size
                logger.info(f"Removed {file_path} to free up space")
                
                if freed_space >= needed_space:
                    return True
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")
        
        return False 