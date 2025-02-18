"""Segment processor module for processing transcripts into segments.

Uses Deepgram's built-in segmentation (paragraphs and speaker changes) and enriches
with OpenAI embeddings and summaries.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
import openai
from openai import OpenAI
import time
from contextlib import contextmanager
import json
import asyncio
from uuid import UUID

from src.config import settings
from src.pipeline.models import Video, VideoStatus, Segment
from src.api.database import db

@contextmanager
def track_progress(task_name: str, video_id: str = None):
    """Context manager for tracking task progress with timing."""
    start_time = time.time()
    task_id = f"{task_name}:{video_id}" if video_id else task_name
    
    try:
        logger.info(f"[PROGRESS] Started {task_id}")
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"[PROGRESS] Completed {task_id} in {duration:.2f}s")

class SegmentProcessor:
    """Processes transcripts into segments using Deepgram's segmentation."""
    
    def __init__(self):
        """Initialize the segment processor."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.min_segment_length = 50  # minimum words for summary generation
        self.max_segment_length = 200  # maximum words before forcing a break
        self.min_segment_duration = 1.0  # minimum segment duration in seconds
        self.max_segment_duration = 30.0  # maximum segment duration in seconds

    async def process_video(self, video_id: UUID) -> None:
        """Process a video by segmenting its transcript and generating summaries."""
        try:
            # Get video transcription
            transcription = await self._get_transcription(video_id)
            if not transcription:
                raise Exception(f"No transcription found for video {video_id}")

            logger.info(f"Processing video {video_id} with transcription")

            # Generate segments from transcription
            segments = await self.process_transcript(video_id, transcription.raw_response)
            if not segments:
                raise Exception(f"Failed to generate segments for video {video_id}")

            logger.info(f"Generated {len(segments)} segments for video {video_id}")

            # Generate embeddings for segments
            segments = await self._generate_embeddings(segments)
            if not segments:
                raise Exception(f"Failed to generate embeddings for video {video_id}")

            logger.info(f"Generated embeddings for {len(segments)} segments")

            # Save segments to database
            await self._save_segments(video_id, segments)
            logger.info(f"Saved {len(segments)} segments to database")

            # Generate comprehensive summary
            summary_data = await self._generate_comprehensive_summary(segments)
            if summary_data:
                await self._update_video_summary(video_id, summary_data)
                logger.info(f"Generated and saved comprehensive summary for video {video_id}")
            else:
                logger.error(f"Failed to generate summary for video {video_id}")

            # Update video status to COMPLETED
            result = db.supabase.table("videos").update({
                "status": VideoStatus.COMPLETED.value,
                "progress": 100,
                "error": None  # Clear any previous errors
            }).eq("id", str(video_id)).execute()

            if not result.data:
                raise Exception("Failed to update video status to COMPLETED")

            logger.info(f"Successfully processed video {video_id}")

        except Exception as e:
            error_msg = f"Failed to process video {video_id}: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            # Update video status to FAILED
            try:
                db.supabase.table("videos").update({
                    "status": VideoStatus.FAILED.value,
                    "error": error_msg,
                    "progress": 0
                }).eq("id", str(video_id)).execute()
            except Exception as update_error:
                logger.error(f"Failed to update video status: {update_error}")
            raise

    async def process_transcript(self, video_id: UUID, transcript_data: dict) -> List[Segment]:
        """Process transcript into segments using Deepgram's paragraph and speaker segmentation."""
        if not transcript_data or "results" not in transcript_data:
            logger.error(f"Invalid transcript data for video {video_id}")
            return []

        try:
            # Extract paragraphs from Deepgram response
            paragraphs = self._extract_paragraphs(transcript_data)
            if not paragraphs:
                logger.error(f"No paragraphs found in transcript for video {video_id}")
                return []

            # Create segments from paragraphs
            segments = []
            for para in paragraphs:
                segment = await self._create_segment(video_id, para)
                if segment:
                    segments.append(segment)

            # Save all segments to database
            if segments:
                await self._save_segments(segments)
                logger.info(f"Saved {len(segments)} segments for video {video_id}")
                
                # Generate video summary and title
                summary = self._generate_video_summary(segments)
                if summary:
                    # Update video with summary and title
                    await self._update_video_summary(video_id, summary)
                    logger.info(f"Updated video {video_id} with summary")
            else:
                logger.warning(f"No valid segments created for video {video_id}")
            
            return segments

        except Exception as e:
            logger.error(f"Failed to process transcript for video {video_id}: {e}")
            logger.exception(e)  # Log full traceback
            return []

    def _extract_paragraphs(self, transcript_data: dict) -> List[Dict]:
        """Extract paragraphs from Deepgram response using their built-in segmentation."""
        try:
            results = transcript_data["results"]
            channels = results.get("channels", [])
            if not channels:
                return []

            paragraphs = []
            current_para = None
            current_word_count = 0
            
            # Get words with timing and speaker information
            words = channels[0].get("alternatives", [{}])[0].get("words", [])
            
            for word in words:
                if not current_para:
                    current_para = {
                        "start_time": word["start"],
                        "end_time": word["end"],
                        "text": word["word"],
                        "speaker": word.get("speaker", "unknown"),
                        "words": [word]
                    }
                    current_word_count = 1
                    continue

                # Check for segment breaks
                time_gap = word["start"] - current_para["end_time"]
                is_new_speaker = word.get("speaker") != current_para["speaker"]
                duration = current_para["end_time"] - current_para["start_time"]
                
                # Force break if:
                # 1. Speaker changes
                # 2. Long pause (>1s)
                # 3. Segment too long (>200 words or >30s)
                if (is_new_speaker or 
                    time_gap > 1.0 or 
                    current_word_count >= self.max_segment_length or
                    duration >= self.max_segment_duration):
                    
                    # Only add if meets minimum requirements
                    if (current_word_count >= 3 and  # at least 3 words
                        duration >= self.min_segment_duration):  # at least 1 second
                        paragraphs.append(current_para)
                    
                    current_para = {
                        "start_time": word["start"],
                        "end_time": word["end"],
                        "text": word["word"],
                        "speaker": word.get("speaker", "unknown"),
                        "words": [word]
                    }
                    current_word_count = 1
                else:
                    current_para["end_time"] = word["end"]
                    current_para["text"] += " " + word["word"]
                    current_para["words"].append(word)
                    current_word_count += 1

            # Add the last paragraph if it meets minimum requirements
            if current_para and current_word_count >= 3:
                duration = current_para["end_time"] - current_para["start_time"]
                if duration >= self.min_segment_duration:
                    paragraphs.append(current_para)

            return paragraphs

        except Exception as e:
            logger.error(f"Failed to extract paragraphs: {e}")
            return []

    async def _create_segment(self, video_id: UUID, para: Dict) -> Optional[Segment]:
        """Create a segment from a paragraph with OpenAI enrichment."""
        try:
            # Generate embedding
            embedding = await self._generate_embedding(para["text"])
            if not embedding or len(embedding) != 1536:
                logger.error(f"Invalid embedding generated for segment in video {video_id}")
                # Return segment without embedding for now, we can update it later
                embedding = [0.0] * 1536  # Use zero vector as fallback

            # Create segment object
            segment = Segment(
                video_id=video_id,
                start_time=para["start_time"],
                end_time=para["end_time"],
                text=para["text"],
                speaker_id=para["speaker"],
                embedding=embedding,
                display_text=para["text"],  # Use original text as display text
                metadata={
                    "word_count": len(para["words"]),
                    "duration": para["end_time"] - para["start_time"],
                    "speaker": para["speaker"],
                    "confidence": sum(w.get("confidence", 0) for w in para["words"]) / len(para["words"])
                }
            )
            
            return segment

        except Exception as e:
            logger.error(f"Failed to create segment: {str(e)}")
            logger.exception(e)  # Log full traceback
            return None

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI's text-embedding-3-small model."""
        try:
            # Ensure text is not empty
            if not text or not text.strip():
                logger.error("Cannot generate embedding for empty text")
                return []

            # Log the request for debugging
            logger.debug(f"Generating embedding for text (length: {len(text)})")
            
            # Create embedding - Note: OpenAI v1.x client is synchronous
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=1536
            )

            # Validate response
            if not response or not response.data or len(response.data) == 0:
                logger.error("No embedding data received from OpenAI")
                return []

            # Extract embedding
            embedding = response.data[0].embedding
            if not embedding or len(embedding) != 1536:
                logger.error(f"Invalid embedding received: length={len(embedding) if embedding else 0}")
                return []

            logger.debug(f"Successfully generated embedding (length: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            logger.exception(e)  # Log full traceback
            return []

    def _generate_video_summary(self, segments: List[Segment]) -> Optional[Dict[str, str]]:
        """Generate a summary and title for the entire video content."""
        try:
            # Combine all segments text with proper context
            full_text = "\n\n".join([
                f"[{s.speaker_id}]: {s.text}" for s in segments
            ])

            # Generate comprehensive summary
            summary_completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze this video transcript and provide:
1. A concise title (5-8 words)
2. A brief summary (2-3 sentences)
3. Key points (3-5 bullet points)

Format the response as:
Title: [title]
Summary: [summary]
Key Points:
- [point 1]
- [point 2]
- [point 3]"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate a summary for this video transcript:\n\n{full_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            summary_text = summary_completion.choices[0].message.content.strip()
            
            # Parse the response into components
            lines = summary_text.split('\n')
            result = {
                'title': '',
                'summary': '',
                'key_points': []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('Title:'):
                    current_section = 'title'
                    result['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Summary:'):
                    current_section = 'summary'
                    result['summary'] = line.replace('Summary:', '').strip()
                elif line.startswith('Key Points:'):
                    current_section = 'key_points'
                elif line.startswith('- ') and current_section == 'key_points':
                    result['key_points'].append(line.replace('- ', '').strip())
                elif line and current_section in ['summary', 'key_points']:
                    if current_section == 'summary':
                        result['summary'] += ' ' + line
            
            logger.info(f"Generated video summary with {len(result['key_points'])} key points")
            return result

        except Exception as e:
            logger.error(f"Failed to generate video summary: {e}")
            logger.exception(e)
            return None

    async def _save_segments(self, segments: List[Segment]) -> None:
        """Save segments to database."""
        try:
            if not segments:
                logger.warning("No segments to save")
                return

            segment_data = []
            for segment in segments:
                # Log segment details for debugging
                logger.debug(f"Preparing segment: start={segment.start_time}, end={segment.end_time}, words={segment.metadata['word_count']}")
                
                # Validate embedding
                if not segment.embedding or len(segment.embedding) != 1536:
                    logger.error(f"Invalid embedding for segment: {len(segment.embedding) if segment.embedding else 0} dimensions")
                    continue

                data = {
                    "video_id": str(segment.video_id),
                    "start_time": float(segment.start_time),  # Ensure float type
                    "end_time": float(segment.end_time),      # Ensure float type
                    "text": str(segment.text),
                    "speaker_id": str(segment.speaker_id),
                    "embedding": segment.embedding,
                    "display_text": str(segment.display_text) if segment.display_text else str(segment.text),
                    "metadata": {
                        "word_count": int(segment.metadata["word_count"]),
                        "duration": float(segment.metadata["duration"]),
                        "speaker": str(segment.metadata["speaker"]),
                        "confidence": float(segment.metadata["confidence"])
                    }
                }
                segment_data.append(data)

            if segment_data:
                logger.info(f"Attempting to save {len(segment_data)} segments to database")
                # Log first segment for debugging
                logger.debug(f"Sample segment data: {json.dumps(segment_data[0], default=str)[:500]}...")
                
                try:
                    result = db.supabase.table("segments").insert(segment_data).execute()
                    if not result.data:
                        logger.error("No data returned from segment insert")
                        logger.error(f"Supabase response: {result}")
                        raise Exception("Failed to insert segments: no data returned")
                    
                    logger.info(f"Successfully saved {len(result.data)} segments")
                    # Log IDs of saved segments
                    segment_ids = [s.get('id') for s in result.data if s.get('id')]
                    logger.debug(f"Saved segment IDs: {segment_ids}")
                    
                except Exception as db_error:
                    logger.error(f"Database error while saving segments: {str(db_error)}")
                    logger.error(f"Error type: {type(db_error).__name__}")
                    raise
        except Exception as e:
            logger.error(f"Failed to save segments: {str(e)}")
            logger.exception(e)  # Log full traceback
            raise 

    async def _generate_comprehensive_summary(self, segments: List[Segment]) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive summary of the video content."""
        try:
            # Combine all segments text with speaker context
            full_text = "\n\n".join([
                f"[Speaker {s.speaker_id}]: {s.text}" for s in segments
            ])

            # Calculate speaker statistics
            speaker_stats = {}
            total_duration = 0
            for segment in segments:
                speaker = str(segment.speaker_id)
                duration = segment.end_time - segment.start_time
                total_duration += duration
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {
                        "total_time": 0,
                        "word_count": 0,
                        "segments": 0
                    }
                speaker_stats[speaker]["total_time"] += duration
                speaker_stats[speaker]["word_count"] += segment.metadata.get("word_count", 0)
                speaker_stats[speaker]["segments"] += 1

            # Calculate word frequencies
            word_freq = {}
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            for segment in segments:
                words = segment.text.lower().split()
                for word in words:
                    if len(word) > 3 and word not in stop_words:
                        word_freq[word] = word_freq.get(word, 0) + 1

            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

            # Generate summary using GPT-4
            summary_prompt = f"""Analyze this video transcript and provide:
1. A concise title (5-8 words)
2. A comprehensive summary (2-3 paragraphs)
3. Key points (4-6 bullet points)
4. Key insights and takeaways
5. Timeline highlights (important moments)

Transcript:
{full_text}

Format the response as JSON:
{{
    "title": "...",
    "summary": "...",
    "key_points": ["...", "..."],
    "insights": ["...", "..."],
    "timeline_highlights": [
        {{"time": "MM:SS", "description": "..."}}
    ]
}}"""

            try:
                summary_completion = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert video content analyzer. Provide clear, concise, and insightful analysis."
                        },
                        {
                            "role": "user",
                            "content": summary_prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                    response_format={ "type": "json_object" }
                )
                
                summary_text = summary_completion.choices[0].message.content
                summary_data = json.loads(summary_text)
                
                # Log successful summary generation
                logger.info("Successfully generated GPT-4 summary")
                logger.debug(f"Summary data: {json.dumps(summary_data, default=str)[:500]}...")
                
            except Exception as gpt_error:
                logger.error(f"Failed to generate GPT-4 summary: {str(gpt_error)}")
                # Provide default values if GPT-4 fails
                summary_data = {
                    "title": "Video Transcript Analysis",
                    "summary": "Automated summary generation failed. Please check the segments for content.",
                    "key_points": [],
                    "insights": [],
                    "timeline_highlights": []
                }
            
            # Combine everything into a comprehensive result
            return {
                "title": summary_data.get("title", "Untitled Video"),
                "summary": summary_data.get("summary", ""),
                "key_points": summary_data.get("key_points", []),
                "timeline_highlights": summary_data.get("timeline_highlights", []),
                "speaker_statistics": speaker_stats,
                "top_keywords": [{"word": word, "frequency": freq} for word, freq in top_keywords],
                "metadata": {
                    "total_duration": total_duration,
                    "total_segments": len(segments),
                    "speaker_count": len(speaker_stats),
                    "average_segment_duration": total_duration / len(segments) if segments else 0,
                    "language": segments[0].metadata.get("language", "unknown") if segments else "unknown"
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate comprehensive summary: {e}")
            logger.exception(e)
            return None

    async def _update_video_summary(self, video_id: UUID, summary_data: Dict[str, Any]) -> None:
        """Update video with generated summary and insights."""
        try:
            if not summary_data:
                logger.warning(f"No summary data to update for video {video_id}")
                return

            # Structure the metadata properly
            metadata = {
                "summary": summary_data.get("summary", ""),
                "key_points": summary_data.get("key_points", []),
                "insights": {  # Nest insights data in a dedicated object
                    "timeline_highlights": summary_data.get("timeline_highlights", []),
                    "speaker_statistics": summary_data.get("speaker_statistics", {}),
                    "top_keywords": summary_data.get("top_keywords", []),
                    "analysis": summary_data.get("metadata", {})
                }
            }

            # Log the metadata structure for debugging
            logger.debug(f"Updating video {video_id} with metadata structure: {json.dumps(metadata, default=str)[:500]}...")

            # Update video with structured metadata
            result = db.supabase.table("videos").update({
                "title": summary_data.get("title", "Untitled Video"),
                "metadata": metadata
            }).eq("id", str(video_id)).execute()
            
            if not result.data:
                raise Exception("Failed to update video summary in database")
            
            logger.info(f"Updated summary and insights for video {video_id}")
            
        except Exception as e:
            logger.error(f"Failed to update video summary: {e}")
            logger.exception(e)
            raise

    async def _get_transcription(self, video_id: UUID) -> Optional[dict]:
        """Get transcription for a video."""
        try:
            result = db.supabase.table("transcriptions").select("*").eq("video_id", str(video_id)).execute()
            if not result.data:
                logger.error(f"No transcription found for video {video_id}")
                return None
            return result.data[0]
        except Exception as e:
            logger.error(f"Error getting transcription: {e}")
            return None

    async def _generate_embeddings(self, segments: List[Segment]) -> List[Segment]:
        """Generate embeddings for segments."""
        try:
            for segment in segments:
                embedding = await self._generate_embedding(segment.text)
                if embedding:
                    segment.embedding = embedding
                else:
                    logger.error(f"Failed to generate embedding for segment {segment.id}")
            return segments
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [] 