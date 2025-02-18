"""Transcriber module for transcribing audio using Deepgram.

This module provides functionality to transcribe audio files using the Deepgram API.
It includes support for:
- Audio format validation (mono, 16kHz, 16-bit WAV)
- Automatic retries with exponential backoff
- Progress tracking and detailed logging
- Database integration for storing transcriptions
- Korean language support with the base model

Example:
    ```python
    transcriber = DeepgramTranscriber()
    transcription = await transcriber.transcribe(video, audio_path)
    ```
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
import json
from loguru import logger
import wave
import httpx
import aiofiles
from uuid import UUID, uuid4

from src.config import settings as default_settings
from src.pipeline.models import Video, VideoStatus, Transcription
from src.api.database import db


class DeepgramTranscriber:
    """Transcribes audio using Deepgram API."""

    def __init__(self, settings=None):
        """Initialize the transcriber."""
        self.settings = settings or default_settings
        self.max_retries = 3
        self.timeout = 300  # 5 minutes
        
        self.api_key = self.settings.services.DEEPGRAM_API_KEY
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
            
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url="https://api.deepgram.com/v1",
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )

    async def _send_to_deepgram(self, audio_path: Path, language: str = "auto") -> Optional[Dict[str, Any]]:
        """Send audio to Deepgram API."""
        if not audio_path:
            raise ValueError("audio_path is required")
            
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav"
        }
        
        # Updated parameters according to Deepgram API docs
        params = {
            "model": "nova-2",  # Using nova-2 model which supports auto language detection
            "smart_format": "true",
            "punctuate": "true",
            "diarize": "true",
            "utterances": "true",
            "detect_language": "true"
        }
        
        try:
            # First log the file size
            file_size = os.path.getsize(audio_path)
            logger.info(f"Audio file size: {file_size / 1024 / 1024:.2f} MB")
            
            async with aiofiles.open(audio_path, "rb") as audio:
                audio_data = await audio.read()
                
                logger.info(f"Sending request to Deepgram for {audio_path}")
                logger.info(f"Request parameters: {params}")
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        "https://api.deepgram.com/v1/listen",
                        content=audio_data,
                        headers=headers,
                        params=params
                    )
                    
                    # Log the raw response for debugging
                    raw_response = response.text
                    logger.debug(f"Raw Deepgram response: {raw_response[:1000]}...")
                    
                    if response.status_code != 200:
                        logger.error(f"Deepgram API error: {response.status_code}")
                        logger.error(f"Response headers: {dict(response.headers)}")
                        logger.error(f"Response body: {raw_response}")
                        return None
                        
                    try:
                        result = response.json()
                        # Log successful response structure and detected language
                        logger.info(f"Successful response from Deepgram. Response structure:")
                        logger.info(f"- Has results: {bool(result.get('results'))}")
                        
                        # Log detected language
                        if result.get('results') and result['results'].get('channels'):
                            detected_language = result['results'].get('detected_language')
                            logger.info(f"- Detected language: {detected_language}")
                            
                            channels = result['results'].get('channels', [])
                            logger.info(f"- Number of channels: {len(channels)}")
                            if channels:
                                alternatives = channels[0].get('alternatives', [])
                                logger.info(f"- Number of alternatives: {len(alternatives)}")
                                if alternatives:
                                    transcript = alternatives[0].get('transcript', '')
                                    logger.info(f"- Has transcript: {bool(transcript)}")
                                    logger.info(f"- Transcript length: {len(transcript)}")
                                    logger.info(f"- First 100 chars: {transcript[:100]}")
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response: {raw_response}")
                        return None
                
        except httpx.TimeoutException:
            logger.error(f"Deepgram request timed out after {self.timeout}s")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Deepgram API error: {str(e)}")
            if e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error processing audio for Deepgram: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return None

    async def _save_transcription(self, video_id: UUID, transcription_data: dict) -> Optional[Transcription]:
        """Save transcription to database."""
        if not transcription_data or not transcription_data.get("results"):
            logger.error(f"No transcription data to save for video {video_id}")
            return None

        try:
            # Extract detected language
            detected_language = transcription_data.get("results", {}).get("detected_language", "unknown")
            
            # Let the database generate the ID using its sequence
            data = {
                "video_id": str(video_id),
                "raw_response": transcription_data,
                "processed_data": None,
                "metadata": {
                    "detected_language": detected_language,
                    "model": "base",
                    "version": "latest"
                }
            }
            
            result = db.supabase.table("transcriptions").insert(data).execute()
            if result.data:
                logger.info(f"Saved transcription for video {video_id} (language: {detected_language})")
                return Transcription(**result.data[0])
            else:
                logger.error("No data returned from transcription insert")
                return None
        except Exception as e:
            logger.error(f"Failed to save transcription: {str(e)}")
            return None

    async def transcribe(self, video: Video, audio_path: Path) -> Optional[Dict[str, Any]]:
        """Transcribe audio using Deepgram with retries."""
        if not await self._validate_audio_format(audio_path):
            raise ValueError(f"Invalid audio format for {audio_path}")
            
        attempts = 0
        transcription_data = None
        
        while attempts < self.max_retries and transcription_data is None:
            attempts += 1
            logger.info(f"Attempt {attempts} to transcribe video {video.id} using model 'base'")
            
            transcription_data = await self._send_to_deepgram(audio_path)
            
            if transcription_data is None:
                logger.error(f"Attempt {attempts} failed: No response received from Deepgram")
                if attempts < self.max_retries:
                    await asyncio.sleep(2 ** attempts)
                continue
            
            # Validate that we have a non-empty transcript
            alternative = transcription_data.get("results", {}) \
                                        .get("channels", [{}])[0] \
                                        .get("alternatives", [{}])[0]
            
            if not alternative.get("transcript"):
                logger.error("Empty transcript received from Deepgram")
                transcription_data = None
                if attempts < self.max_retries:
                    await asyncio.sleep(2 ** attempts)
                continue
            
            # Save successful transcription
            await self._save_transcription(video.id, transcription_data)
            logger.info(f"Successfully transcribed video {video.id} (confidence: {alternative.get('confidence', 0)})")
            return transcription_data
        
        logger.error(f"Failed to get valid transcript after {attempts} attempts")
        return None

    async def _validate_audio_format(self, audio_path: Path) -> bool:
        """Validate audio file format meets Deepgram requirements."""
        try:
            if not await self._validate_audio_file(audio_path):
                return False
                
            with wave.open(str(audio_path), 'rb') as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                
                logger.debug(f"Audio format: {channels} channels, {sample_rate}Hz, {sample_width*8}-bit")
                
                if channels != 1:
                    logger.error(f"Invalid audio channels: {channels} (must be mono)")
                    return False
                if sample_rate not in [16000, 44100, 48000]:
                    logger.error(f"Unsupported sample rate: {sample_rate}Hz (must be 16kHz, 44.1kHz, or 48kHz)")
                    return False
                if sample_width != 2:  # 16-bit
                    logger.error(f"Invalid bit depth: {sample_width*8}-bit (must be 16-bit)")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error validating audio format: {str(e)}")
            return False

    async def _validate_audio_file(self, audio_path: Path) -> bool:
        """Validate that the audio file exists and is readable."""
        try:
            if not audio_path.exists():
                logger.error(f"Audio file does not exist: {audio_path}")
                return False
            
            if not audio_path.is_file():
                logger.error(f"Audio path is not a file: {audio_path}")
                return False
            
            # Try to open the file to verify it's readable
            with open(audio_path, 'rb') as f:
                # Read first few bytes to verify file is accessible
                f.read(1024)
            
            return True
        except Exception as e:
            logger.error(f"Error validating audio file {audio_path}: {str(e)}")
            return False

    async def _get_existing_transcription(self, video_id: int) -> Optional[Transcription]:
        """Check if transcription already exists."""
        try:
            response = db.supabase.table("transcriptions").select("*").eq("video_id", video_id).execute()
            if response.data:
                return Transcription(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to check existing transcription: {e}")
            raise

    async def _update_video_status(self, video: Video) -> None:
        """Update video status in database."""
        try:
            data = {"status": video.status.value}
            if hasattr(video, 'error') and video.error:
                data["error"] = video.error
            db.supabase.table("videos").update(data).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise