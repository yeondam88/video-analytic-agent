from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.pipeline.coordinator import PipelineCoordinator
from src.pipeline.models import Video, VideoStatus
from src.db.database import db

app = FastAPI(title="Video Analytics API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline coordinator
coordinator = PipelineCoordinator()


@app.get("/videos")
async def list_videos():
    """List all videos in the library"""
    try:
        response = await db.client.table("videos").select("*").order("created_at", desc=True).execute()
        return [Video(**video).model_dump() for video in response.data]
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to list videos")


@app.get("/videos/{video_id}")
async def get_video(video_id: int):
    """Get video details with transcripts and segments"""
    try:
        # Get video
        video_response = await db.client.table("videos").select("*").eq("id", video_id).execute()
        if not video_response.data:
            raise HTTPException(status_code=404, detail="Video not found")
        video = Video(**video_response.data[0])
        
        # Get transcript
        transcript_response = await db.client.table("transcriptions").select("*").eq("video_id", video_id).execute()
        transcript = transcript_response.data[0] if transcript_response.data else None
        
        # Get segments
        segments_response = await db.client.table("segments").select("*").eq("video_id", video_id).order("start_time").execute()
        segments = segments_response.data if segments_response.data else []
        
        return {
            "video": video.model_dump(),
            "transcript": transcript,
            "segments": segments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video details")


@app.post("/videos")
async def create_video(video: Video, background_tasks: BackgroundTasks):
    """Create a new video and start processing"""
    try:
        # Insert video
        data = video.model_dump(exclude={'id', 'created_at', 'updated_at'})
        response = await db.client.table("videos").insert(data).execute()
        video_id = response.data[0]['id']
        
        # Start processing in background
        background_tasks.add_task(coordinator.process_video, video_id)
        
        return {"id": video_id, "message": "Video processing started"}
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        raise HTTPException(status_code=500, detail="Failed to create video")


@app.get("/videos/{video_id}/status")
async def get_video_status(video_id: int):
    """Get video processing status"""
    try:
        response = await db.client.table("videos").select("status").eq("id", video_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"status": response.data[0]['status']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video status") 