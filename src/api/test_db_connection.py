import logging
import sys
from pathlib import Path
import os
import asyncio

import psycopg2
from loguru import logger
from sqlalchemy import create_engine, text
from supabase import create_client, Client

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add the project root to sys.path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.api.config.settings import Settings, settings
from src.api.database import db, DatabaseError
from src.pipeline.models import Video, VideoStatus, VideoSource

async def test_database_connection():
    """Test database connection and basic operations."""
    try:
        logger.info("Testing database connection...")
        
        # Test basic connection by listing videos
        logger.info("Testing basic query...")
        videos = await db.list("videos", limit=1)
        logger.info("Successfully queried database")
        
        # Test video creation
        logger.info("Testing record creation...")
        test_video = {
            "source": VideoSource.LOOM.value,
            "source_id": "test_video_123",
            "url": "https://example.com/test",
            "title": "Test Video",
            "status": VideoStatus.PENDING.value
        }
        
        # Clean up any existing test data
        logger.info("Cleaning up existing test data...")
        await db.supabase.table("videos").delete().eq("source_id", "test_video_123").execute()
        
        # Create test video
        logger.info("Creating test video...")
        created = await db.create("videos", test_video)
        if not created:
            raise DatabaseError("Failed to create test video")
        video_id = created["id"]
        logger.info(f"Successfully created test video with ID: {video_id}")
        
        # Read test video
        logger.info("Testing record retrieval...")
        retrieved = await db.read("videos", video_id)
        if not retrieved:
            raise DatabaseError("Failed to retrieve test video")
        logger.info("Successfully retrieved test video")
        
        # Update test video
        logger.info("Testing record update...")
        updated = await db.update("videos", video_id, {"status": VideoStatus.COMPLETED.value})
        if not updated:
            raise DatabaseError("Failed to update test video")
        logger.info("Successfully updated test video")
        
        # Delete test video
        logger.info("Testing record deletion...")
        deleted = await db.delete("videos", video_id)
        if not deleted:
            raise DatabaseError("Failed to delete test video")
        logger.info("Successfully deleted test video")
        
        logger.info("All database tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection()) 