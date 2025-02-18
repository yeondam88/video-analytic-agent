from typing import List, Optional, Dict, Any
import numpy as np
from loguru import logger
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config import settings
from src.db.models import Segment


class EmbeddingService:
    def __init__(self, db: Session):
        self.db = db
        api_key = settings.services.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = settings.services.OPENAI_EMBEDDING_MODEL
        self.embedding_dimension = 1536  # Dimension of the embedding vector

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using OpenAI's API."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def update_segment_embedding(self, segment_id: int, text: str) -> bool:
        """Update the embedding for a specific segment."""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text)
            
            # Update segment in database
            self.db.execute(
                text("UPDATE segments SET embedding = :embedding WHERE id = :id"),
                {"embedding": embedding, "id": segment_id}
            )
            self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to update segment embedding: {e}")
            self.db.rollback()
            return False

    async def search_similar_segments(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for segments similar to the query text."""
        try:
            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)
            
            # Perform vector similarity search
            result = self.db.execute(
                text("""
                    SELECT 
                        s.id,
                        s.video_id,
                        s.text,
                        s.start_time,
                        s.end_time,
                        s.speaker_id,
                        1 - (s.embedding <=> :embedding) as similarity
                    FROM segments s
                    WHERE s.embedding IS NOT NULL
                    AND s.deleted_at IS NULL
                    ORDER BY s.embedding <=> :embedding
                    LIMIT :limit
                """),
                {
                    "embedding": query_embedding,
                    "limit": limit
                }
            )
            
            # Convert results to list of dictionaries
            segments = []
            for row in result:
                if row.similarity >= threshold:
                    segments.append({
                        "id": row.id,
                        "video_id": row.video_id,
                        "text": row.text,
                        "start_time": row.start_time,
                        "end_time": row.end_time,
                        "speaker_id": row.speaker_id,
                        "similarity": float(row.similarity)
                    })
            
            return segments
        except Exception as e:
            logger.error(f"Failed to search similar segments: {e}")
            return []

    async def batch_update_embeddings(self, segment_ids: List[int]) -> bool:
        """Update embeddings for multiple segments in batch."""
        try:
            # Get segments without embeddings
            segments = (
                self.db.query(Segment)
                .filter(Segment.id.in_(segment_ids))
                .all()
            )
            
            for segment in segments:
                if not segment.embedding:
                    success = await self.update_segment_embedding(
                        segment.id,
                        segment.text
                    )
                    if not success:
                        logger.warning(f"Failed to update embedding for segment {segment.id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to batch update embeddings: {e}")
            return False 