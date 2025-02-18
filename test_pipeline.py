import asyncio
from loguru import logger
from src.pipeline.coordinator import PipelineCoordinator
from src.api.database import db
from src.pipeline.types import VideoStatus, VideoSource

# Test video URLs - one from Loom and one from YouTube
TEST_VIDEOS = [
    {
        "url": "https://www.loom.com/share/68c32e1a9a974e3f99075b3e70c7c7fc",  # Public demo video
        "source": VideoSource.LOOM.value,
        "source_id": "68c32e1a9a974e3f99075b3e70c7c7fc",
        "title": "Test Loom Video",
        "description": "Test video for pipeline",
        "status": VideoStatus.PENDING.value,
        "progress": 0,
        "steps_completed": [],
        "processing_details": []
    },
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Public YouTube video
        "source": VideoSource.YOUTUBE.value,
        "source_id": "dQw4w9WgXcQ",
        "title": "Test YouTube Video",
        "description": "Test video for pipeline",
        "status": VideoStatus.PENDING.value,
        "progress": 0,
        "steps_completed": [],
        "processing_details": []
    }
]

async def test_pipeline(test_video_data=None):
    """Test the video processing pipeline."""
    results = []
    
    try:
        # Process each test video
        for video_data in TEST_VIDEOS if test_video_data is None else [test_video_data]:
            try:
                # Create video record
                result = db.supabase.table("videos").insert(video_data).execute()
                video_id = result.data[0]['id']
                logger.info(f"Created test video with ID: {video_id}")
                
                # Initialize pipeline
                coordinator = PipelineCoordinator()
                
                # Process video
                success = await coordinator.process_video(video_id)
                
                # Get final video status
                result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
                final_video = result.data[0]
                
                logger.info(f"Final video status: {final_video['status']}")
                logger.info(f"Progress: {final_video['progress']}%")
                logger.info(f"Steps completed: {final_video['steps_completed']}")
                
                if final_video['status'] == VideoStatus.FAILED.value:
                    error = final_video.get('error', 'Unknown error')
                    logger.error(f"Error processing {video_data['source']} video: {error}")
                    results.append({
                        'source': video_data['source'],
                        'success': False,
                        'error': error
                    })
                else:
                    logger.info(f"Successfully processed {video_data['source']} video")
                    results.append({
                        'source': video_data['source'],
                        'success': True
                    })
                
            except Exception as e:
                logger.error(f"Failed to process {video_data['source']} video: {e}")
                results.append({
                    'source': video_data['source'],
                    'success': False,
                    'error': str(e)
                })
                
            finally:
                # Clean up database
                try:
                    db.supabase.table("videos").delete().eq("source_id", video_data["source_id"]).execute()
                except Exception as e:
                    logger.error(f"Failed to clean up video record: {e}")
        
        # Return overall success only if all videos processed successfully
        return all(result['success'] for result in results)
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_pipeline()) 