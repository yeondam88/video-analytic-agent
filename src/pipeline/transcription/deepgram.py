"""Deepgram transcription service."""
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from deepgram import Deepgram, PrerecordedOptions

from src.config import settings
from src.api.database import db
from src.pipeline.models import Video, VideoStatus


class DeepgramTranscriber:
    """Transcribes audio using Deepgram's API."""

    def __init__(self):
        """Initialize the Deepgram client."""
        api_key = settings.services.DEEPGRAM_API_KEY
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
        self.client = Deepgram(api_key)

    async def transcribe(self, video: Video, audio_path: Path) -> Optional[Dict[Any, Any]]:
        """Transcribe audio file using Deepgram."""
        try:
            # Update video status
            video.status = VideoStatus.TRANSCRIBING
            await self._update_video_status(video)

            # Configure transcription options
            options = PrerecordedOptions(
                model=settings.services.DEEPGRAM_MODEL,  # Use model from settings
                smart_format=True,
                diarize=True,
                punctuate=True,
                language="en",
                tier="enhanced"
            )

            # Open audio file and send to Deepgram
            with open(str(audio_path), "rb") as audio:
                source = {"buffer": audio, "mimetype": "audio/wav"}
                response = await self.client.transcription.prerecorded(source, options)

                if not response or "results" not in response:
                    logger.error(f"No transcription results for video {video.source_id}")
                    video.status = VideoStatus.FAILED
                    await self._update_video_status(video)
                    return None

                # Store transcription in database
                await self._store_transcription(video, response)
                
                # Update video status
                video.status = VideoStatus.TRANSCRIBED
                await self._update_video_status(video)

                logger.info(f"Successfully transcribed video {video.source_id}")
                return response

        except Exception as e:
            logger.error(f"Failed to transcribe video {video.source_id}: {e}")
            video.status = VideoStatus.FAILED
            await self._update_video_status(video)
            return None

    async def _store_transcription(self, video: Video, transcription: Dict[Any, Any]) -> None:
        """Store transcription results in database."""
        try:
            # Extract relevant data from transcription
            data = {
                "video_id": video.id,
                "text": transcription["results"]["channels"][0]["alternatives"][0]["transcript"],
                "confidence": transcription["results"]["channels"][0]["alternatives"][0]["confidence"],
                "words": transcription["results"]["channels"][0]["alternatives"][0]["words"],
                "metadata": transcription.get("metadata", {}),
            }

            # Store in database
            await db.supabase.table("transcriptions").insert(data).execute()
            logger.info(f"Stored transcription for video {video.source_id}")

        except Exception as e:
            logger.error(f"Failed to store transcription for video {video.source_id}: {e}")
            raise

    async def _update_video_status(self, video: Video) -> None:
        """Update video status in database."""
        try:
            await db.supabase.table("videos").update({
                "status": video.status.value
            }).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise 