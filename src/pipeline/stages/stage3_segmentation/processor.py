"""Segment processor module for processing transcripts into segments.

This module provides functionality to process transcripts into meaningful segments,
including:
- Automatic segment boundary detection based on pauses and speaker changes
- Speaker diarization information handling
- Embedding generation using OpenAI's text-embedding-ada-002 model
- Summary generation for longer segments using GPT-4
- Database integration with pgvector for efficient similarity search

Example:
    ```python
    processor = SegmentProcessor()
    segments = await processor.process_transcript(video, transcript_data)
    ```
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import sys
import openai
from openai import OpenAI
import time
from contextlib import contextmanager
import json
import asyncio
from datetime import datetime

from src.config import settings
from src.pipeline.models import Video, VideoStatus, Segment
from src.api.database import db

# Configure logger to print to stdout
logger.remove()  # Remove default handlers
logger.add(sys.stdout, level="DEBUG")

@contextmanager
def track_progress(task_name: str, video_id: str = None):
    """Context manager for tracking task progress with timing.
    
    Args:
        task_name: Name of the task being tracked
        video_id: Optional video ID for context
        
    Yields:
        None
        
    Example:
        ```python
        with track_progress("embedding_generation", video.id):
            embeddings = await generate_embeddings(segments)
        ```
    """
    start_time = time.time()
    task_id = f"{task_name}:{video_id}" if video_id else task_name
    
    try:
        logger.info(f"[PROGRESS] Started {task_id}")
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"[PROGRESS] Completed {task_id} in {duration:.2f}s")


class SegmentProcessor:
    """Processes transcripts into segments with embeddings and summaries.
    
    This class handles the segmentation of transcripts into meaningful chunks,
    enriching them with embeddings for similarity search and summaries for
    longer segments. It includes:
    - Automatic segment boundary detection
    - Speaker diarization information handling
    - Embedding generation using OpenAI
    - Summary generation using GPT-4
    - Database integration with pgvector
    
    Attributes:
        client: OpenAI client for embeddings and summaries
        batch_size: Number of segments to process in parallel
        min_segment_words: Minimum words required for summary generation
        max_retries: Maximum number of retry attempts for API calls
    """
    
    def __init__(self):
        """Initialize the segment processor."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.batch_size = 10  # Process segments in batches
        self.min_segment_words = 50  # Minimum words for summary
        self.max_retries = 3  # Maximum retry attempts

    def _get_validated_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and extract transcript data."""
        try:
            # Get the raw transcript
            transcript = transcript_data
            if isinstance(transcript_data, dict) and "raw_transcript" in transcript_data:
                logger.debug("Found raw_transcript in transcript_data")
                transcript = transcript_data["raw_transcript"]

            # Parse JSON if needed
            if isinstance(transcript, str):
                logger.debug("Transcript is a string, parsing JSON")
                try:
                    transcript = json.loads(transcript)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse transcript JSON: {e}")

            # Log transcript structure for debugging
            logger.debug("Transcript structure:")
            logger.debug(json.dumps(transcript, indent=2)[:1000] + "...")

            # Extract and validate transcript data
            if not isinstance(transcript, dict):
                raise ValueError(f"Invalid transcript type: {type(transcript)}")

            results = transcript.get("results", {})
            logger.debug(f"Results keys: {list(results.keys())}")
            
            channels = results.get("channels", [])
            logger.debug(f"Number of channels: {len(channels)}")
            if not channels:
                raise ValueError("Transcript missing 'channels'")

            alternatives = channels[0].get("alternatives", [])
            logger.debug(f"Number of alternatives: {len(alternatives)}")
            if not alternatives:
                raise ValueError("Transcript missing 'alternatives'")

            alternative = alternatives[0]
            words = alternative.get("words", [])
            transcript_text = alternative.get("transcript", "").strip()
            
            if not transcript_text:
                raise ValueError("Transcript text is empty")
                
            logger.info(f"Transcript validation successful:")
            logger.info(f"- Text length: {len(transcript_text)} chars")
            logger.info(f"- Words available: {len(words)} words")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Transcript validation failed: {e}")
            raise ValueError(f"Invalid transcript data: {str(e)}")
            
    async def _create_segments(self, video: Video, transcript: Dict[str, Any]) -> List[Segment]:
        """Create segments from transcript data."""
        try:
            alternative = transcript["results"]["channels"][0]["alternatives"][0]
            words = alternative.get("words", [])
            transcript_text = alternative["transcript"].strip()
            
            segments = []
            
            if words:
                # Use word-level information if available
                logger.info("Using word-level segmentation")
                
                # Group words into segments
                WORDS_PER_SEGMENT = 50  # Adjust this value as needed
                current_segment = []
                segment_start = float(words[0].get("start", 0))
                
                for i, word in enumerate(words):
                    current_segment.append(word)
                    
                    # Start new segment if:
                    # 1. Reached desired words per segment
                    # 2. End of sentence and minimum words reached
                    # 3. Last word
                    word_text = word.get("word", "").strip()
                    is_end_of_sentence = word_text.endswith(('.', '!', '?'))
                    is_last_word = i == len(words) - 1
                    
                    if (len(current_segment) >= WORDS_PER_SEGMENT or 
                        (is_end_of_sentence and len(current_segment) >= 10) or 
                        is_last_word):
                        
                        # Create segment
                        segment_text = " ".join(w.get("word", "") for w in current_segment)
                        try:
                            segment = Segment(
                                video_id=video.id,
                                start_time=segment_start,
                                end_time=float(word.get("end", 0)),
                                text=segment_text.strip(),
                                speaker_id=word.get("speaker", "unknown"),
                                display_text=segment_text.strip(),
                                metadata={
                                    "word_count": len(current_segment),
                                    "duration": float(word.get("end", 0)) - segment_start,
                                    "has_word_timing": True
                                }
                            )
                            segments.append(segment)
                            
                        except Exception as e:
                            logger.error(f"Failed to create segment: {e}, data: {segment_text[:100]}...")
                            continue
                        
                        # Reset for next segment
                        current_segment = []
                        if i < len(words) - 1:
                            segment_start = float(words[i + 1].get("start", 0))
                
            else:
                # Fallback: Split transcript text into segments
                logger.info("Falling back to text-based segmentation")
                
                # Split into sentences first
                sentences = [s.strip() for s in transcript_text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
                
                # Group sentences into segments
                CHARS_PER_SEGMENT = 500  # Adjust this value as needed
                current_segment = []
                current_length = 0
                duration = float(transcript.get("metadata", {}).get("duration", 0))
                
                for sentence in sentences:
                    current_segment.append(sentence)
                    current_length += len(sentence)
                    
                    if current_length >= CHARS_PER_SEGMENT:
                        # Create segment
                        segment_text = ". ".join(current_segment) + "."
                        try:
                            segment = Segment(
                                video_id=video.id,
                                start_time=0,  # No timing info available
                                end_time=duration,
                                text=segment_text.strip(),
                                speaker_id="unknown",
                                display_text=segment_text.strip(),
                                metadata={
                                    "word_count": len(segment_text.split()),
                                    "duration": duration,
                                    "has_word_timing": False,
                                    "is_text_only": True
                                }
                            )
                            segments.append(segment)
                            
                        except Exception as e:
                            logger.error(f"Failed to create segment: {e}, data: {segment_text[:100]}...")
                            continue
                        
                        # Reset for next segment
                        current_segment = []
                        current_length = 0
                
                # Add remaining sentences as final segment
                if current_segment:
                    segment_text = ". ".join(current_segment) + "."
                    try:
                        segment = Segment(
                            video_id=video.id,
                            start_time=0,
                            end_time=duration,
                            text=segment_text.strip(),
                            speaker_id="unknown",
                            display_text=segment_text.strip(),
                            metadata={
                                "word_count": len(segment_text.split()),
                                "duration": duration,
                                "has_word_timing": False,
                                "is_text_only": True
                            }
                        )
                        segments.append(segment)
                        
                    except Exception as e:
                        logger.error(f"Failed to create segment: {e}, data: {segment_text[:100]}...")
            
            if not segments:
                raise ValueError("No valid segments could be created from transcript")
                
            logger.info(f"Successfully created {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to create segments: {e}")
            raise ValueError(f"Failed to create segments: {str(e)}")
            
    async def process_transcript(self, video: Video, transcript_data: Dict[str, Any]) -> List[Segment]:
        """Process a transcript into segments with embeddings and summaries."""
        try:
            # Update video status
            video.status = VideoStatus.SEGMENTING
            await self._update_video_status(video)

            # Get and validate transcript data
            transcript = self._get_validated_transcript(transcript_data)
            
            # Create initial segments
            segments = await self._create_segments(video, transcript)
            
            if not segments:
                raise ValueError("No segments could be created from transcript")
                
            # Process segments in batches
            processed_segments = []
            for i in range(0, len(segments), self.batch_size):
                batch = segments[i:i + self.batch_size]
                
                try:
                    # Save batch first to get IDs
                    saved_segments = await self._save_segments(batch)
                    
                    # Now process with embeddings and summaries
                    await self._process_batch(saved_segments)
                    
                    processed_segments.extend(saved_segments)
                    
                    # Update progress
                    progress = min(100, (i + len(batch)) / len(segments) * 100)
                    await self._update_progress(video, progress)
                    
                except Exception as e:
                    logger.error(f"Failed to process batch: {e}")
                    # Continue with next batch

            if not processed_segments:
                raise ValueError("Failed to process any segments")
                
            logger.info(f"Successfully processed {len(processed_segments)} segments")
            return processed_segments

        except Exception as e:
            error_msg = f"Failed to process transcript for video {video.id}: {str(e)}"
            logger.error(error_msg)
            video.status = VideoStatus.FAILED
            video.error = error_msg
            await self._update_video_status(video)
            raise

    async def _save_segments(self, segments: List[Segment]) -> List[Segment]:
        """Save segments to database and return with IDs."""
        try:
            segment_data = []
            for segment in segments:
                data = segment.to_dict()
                data.pop('id', None)
                data.pop('created_at', None)
                data.pop('updated_at', None)
                segment_data.append(data)

            response = db.client.table("segments").insert(segment_data).execute()
            
            # Update segment objects with new IDs
            for segment, row in zip(segments, response.data):
                segment.id = row['id']
                logger.debug(f"Assigned ID {segment.id} to segment")
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to save segments: {e}")
            raise

    async def _generate_embeddings(self, segments: List[Segment]) -> None:
        """Generate embeddings for segments."""
        for segment in segments:
            for attempt in range(self.max_retries):
                try:
                    response = await openai.Embedding.acreate(
                        model="text-embedding-ada-002",
                        input=segment.text
                    )
                    segment.embedding = response["data"][0]["embedding"]
                    logger.debug(f"Generated embedding for segment {segment.id}")
                    break
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to generate embedding for segment {segment.id}: {e}")
                        raise
                    await asyncio.sleep(2 ** attempt)

    async def _generate_summaries(self, segments: List[Segment]) -> None:
        """Generate summaries for segments."""
        for segment in segments:
            if len(segment.text.split()) <= self.min_segment_words:
                continue
                
            for attempt in range(self.max_retries):
                try:
                    messages = [
                        {"role": "system", "content": "Return JSON with 'title' and 'summary' keys."},
                        {"role": "user", "content": f"For this text:\n\n{segment.text}\n\nProvide a title (max 5 words) and one-sentence summary."}
                    ]
                    
                    response = await openai.ChatCompletion.acreate(
                        model="gpt-4",
                        messages=messages,
                        temperature=0.3
                    )
                    
                    try:
                        content = json.loads(response["choices"][0]["message"]["content"])
                        segment.title = content["title"]
                        segment.display_text = content["summary"]
                        segment.metadata.update({
                            "has_summary": True,
                            "summary_generated_at": datetime.now().isoformat()
                        })
                        logger.debug(f"Generated summary for segment {segment.id}")
                        break
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse GPT response for segment {segment.id}: {e}")
                        segment.metadata["has_summary"] = False
                        
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to generate summary for segment {segment.id}: {e}")
                        segment.metadata["has_summary"] = False
                        break
                    await asyncio.sleep(2 ** attempt)

    async def _update_segments(self, segments: List[Segment]) -> None:
        """Update segments in database."""
        try:
            for segment in segments:
                if not segment.id:
                    logger.error(f"Segment missing ID: {segment}")
                    continue
                    
                update_data = {
                    "embedding": segment.embedding,
                    "title": segment.title,
                    "display_text": segment.display_text,
                    "metadata": segment.metadata
                }
                
                db.client.table("segments").update(update_data).eq("id", segment.id).execute()
                logger.debug(f"Updated segment {segment.id}")
                
        except Exception as e:
            logger.error(f"Failed to update segments: {e}")
            raise

    async def _update_video_status(self, video: Video) -> None:
        """Update video status in database.
        
        Args:
            video: Video object with updated status
        """
        try:
            db.client.table("videos").update({
                "status": video.status.value
            }).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise

    async def _update_progress(self, video: Video, progress: float) -> None:
        """Update video processing progress.
        
        Args:
            video: Video object to update
            progress: Progress percentage (0-100)
        """
        try:
            db.client.table("videos").update({
                "progress": progress
            }).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            raise 