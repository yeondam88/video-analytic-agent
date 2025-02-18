"""Transcriber module for transcribing audio using Deepgram.

This module provides functionality to transcribe audio files using the Deepgram API.
It includes support for:
- Audio format validation (mono, 16kHz, 16-bit WAV)
- Automatic retries with exponential backoff
- Progress tracking and detailed logging
- Database integration for storing transcriptions
- Korean language support with the nova-2 model

Example:
    ```python
    transcriber = DeepgramTranscriber()
    transcription = await transcriber.transcribe(video, audio_path)
    ```
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import asyncio
import json
import wave
from loguru import logger

from deepgram import Deepgram
from src.config import settings as default_settings
from src.pipeline.models import Video, VideoStatus, Transcription
from src.api.database import db


class DeepgramTranscriber:
    """Transcribes audio using Deepgram API.
    
    This class handles the transcription of audio files using Deepgram's API,
    with support for Korean language transcription using the nova-2 model.
    It includes automatic retries, progress tracking, and database integration.
    
    Attributes:
        settings: Application settings including API keys and model configuration
        client: Initialized Deepgram client
        max_retries: Maximum number of retry attempts for failed transcriptions
        base_timeout: Base timeout in seconds (doubles with each retry)
    """
    
    def __init__(self, settings=None):
        """Initialize the transcriber with settings."""
        self.settings = settings or default_settings
        api_key = self.settings.services.DEEPGRAM_API_KEY
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
        self.client = Deepgram(api_key)
        self.max_retries = 3
        self.base_timeout = 10  # Base timeout in seconds

    async def transcribe(self, video: Video, audio_path: Path) -> Optional[Dict[str, Any]]:
        """Transcribe audio using Deepgram with retries and proper error handling.
        
        Args:
            video: Video object containing metadata and status information
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Optional[Dict[str, Any]]: Transcription response from Deepgram if successful,
                                    None if transcription fails
            
        The transcription process includes:
        1. Validating audio file format (mono, 16kHz, 16-bit WAV)
        2. Checking for existing transcriptions to avoid duplicates
        3. Transcribing with automatic retries and exponential backoff
        4. Storing results in the database with detailed metadata
        
        Raises:
            ValueError: If audio file is invalid or transcription fails
            TimeoutError: If transcription request times out
        """
        try:
            # Update video status
            video.status = VideoStatus.TRANSCRIBING
            await self._update_video_status(video)

            # Check if transcription already exists
            existing = await self._get_existing_transcription(video.id)
            if existing:
                logger.info(f"Transcription already exists for video {video.source_id}")
                return existing.to_dict()

            # Validate audio file existence and permissions
            if not await self._validate_audio_file(audio_path):
                raise ValueError(f"Invalid or missing audio file: {audio_path}")

            # Validate audio format
            is_valid, message = await self._validate_audio_format(audio_path)
            if not is_valid:
                raise ValueError(f"Audio format validation failed: {message}")
            logger.info(f"Audio format validation passed: {message}")

            # Get file size for logging
            file_size = os.path.getsize(audio_path)
            logger.info(f"Processing audio file: {file_size/1024/1024:.2f}MB")

            for attempt in range(self.max_retries):
                try:
                    # Read the entire file into memory
                    with open(audio_path, 'rb') as audio:
                        audio_data = audio.read()
                        
                    # Configure transcription options
                    source = {
                        'buffer': audio_data,
                        'mimetype': 'audio/wav'
                    }
                    
                    options = {
                        'smart_format': True,
                        'punctuate': True,
                        'diarize': True,
                        'utterances': True,
                        'numerals': True,
                        'model': self.settings.services.DEEPGRAM_MODEL,
                        'language': self.settings.services.DEEPGRAM_LANGUAGE,
                        'tier': 'enhanced'
                    }

                    # Log request details
                    logger.info(f"Attempt {attempt + 1}/{self.max_retries} to transcribe video {video.source_id}")
                    logger.debug(f"Deepgram options: {json.dumps(options)}")
                    
                    # Calculate timeout with exponential backoff
                    timeout = self.base_timeout * (2 ** attempt)
                    logger.info(f"Using timeout of {timeout} seconds")

                    # Use the prerecorded API with proper async/await
                    response = await asyncio.wait_for(
                        self.client.transcription.prerecorded(source, options),
                        timeout=timeout
                    )
                    
                    # Log the raw response for debugging
                    if response:
                        logger.debug(f"Deepgram raw response: {json.dumps(response)[:500]}...")
                    else:
                        logger.error("Received null response from Deepgram")
                        raise ValueError("No response received from Deepgram")
                    
                    if not isinstance(response, dict):
                        raise ValueError(f"Invalid response type from Deepgram: {type(response)}")

                    # Validate response structure
                    if 'results' not in response:
                        raise ValueError(f"Missing 'results' in response: {json.dumps(response)[:200]}...")

                    # Extract transcript data
                    channels = response['results'].get('channels', [])
                    if not channels:
                        raise ValueError("No channels found in transcription response")

                    alternatives = channels[0].get('alternatives', [])
                    if not alternatives:
                        raise ValueError("No alternatives found in transcription response")

                    transcript_data = alternatives[0]
                    confidence = transcript_data.get('confidence', 0)
                    
                    # Store the transcription with detailed metadata
                    transcription = Transcription(
                        video_id=video.id,
                        raw_transcript=response,
                        extra_data={
                            'language': response.get('results', {}).get('detected_language', self.settings.services.DEEPGRAM_LANGUAGE),
                            'language_confidence': response.get('results', {}).get('language_confidence', 1.0),
                            'model_used': self.settings.services.DEEPGRAM_MODEL,
                            'confidence': confidence,
                            'duration': response.get('metadata', {}).get('duration'),
                            'channels': response.get('metadata', {}).get('channels'),
                            'created': response.get('metadata', {}).get('created'),
                            'attempt': attempt + 1,
                            'processing_time': response.get('metadata', {}).get('processing_time'),
                            'file_size_mb': file_size/1024/1024
                        }
                    )
                    await self._save_transcription(transcription)

                    logger.info(f"Successfully transcribed video {video.source_id} "
                              f"(confidence: {confidence:.2f}, attempt: {attempt + 1})")
                    return response

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} "
                                 f"for video {video.source_id} (timeout: {timeout}s)")
                    if attempt == self.max_retries - 1:
                        raise ValueError(f"Transcription timed out after {self.max_retries} attempts")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue

                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                    continue

        except Exception as e:
            error_msg = f"Failed to transcribe video {video.source_id}: {str(e)}"
            logger.error(error_msg)
            video.status = VideoStatus.FAILED
            video.error = error_msg
            await self._update_video_status(video)
            return None

    async def _validate_audio_format(self, audio_path: Path) -> Tuple[bool, str]:
        """Validate audio file format meets Deepgram requirements.
        
        Args:
            audio_path: Path to the audio file to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
                - is_valid: True if format is valid, False otherwise
                - message: Description of validation result or error
                
        Required format:
        - Channels: Mono (1 channel)
        - Sample rate: 16kHz
        - Bit depth: 16-bit
        """
        try:
            with wave.open(str(audio_path), 'rb') as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                
                if channels != 1:
                    return False, f"Invalid audio channels: {channels} (must be mono)"
                if sample_rate != 16000:
                    return False, f"Invalid sample rate: {sample_rate}Hz (must be 16kHz)"
                if sample_width != 2:  # 16-bit
                    return False, f"Invalid bit depth: {sample_width*8}-bit (must be 16-bit)"
                
                return True, "Audio format validation successful"
        except Exception as e:
            return False, f"Invalid audio format: {str(e)}"

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

    async def _save_transcription(self, transcription: Transcription):
        """Save transcription to database."""
        try:
            data = transcription.to_dict()
            data.pop('id', None)  # Remove id as it's auto-generated
            data.pop('created_at', None)  # Remove timestamps as they're handled by the database
            data.pop('updated_at', None)
            db.supabase.table("transcriptions").insert(data).execute()
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            raise

    async def _update_video_status(self, video: Video):
        """Update video status in the database."""
        try:
            db.supabase.table("videos").update({
                "status": video.status.value
            }).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise 