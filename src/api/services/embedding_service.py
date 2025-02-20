from typing import List, Optional, Dict, Any
import numpy as np
from loguru import logger
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session
import meilisearch

from src.config import settings
from src.db.models import Segment


class EmbeddingService:
    def __init__(self, db: Session):
        self.db = db
        try:
            # Initialize Meilisearch client with cloud configuration
            self.client = meilisearch.Client(
                settings.meilisearch.host,
                settings.meilisearch.api_key
            )
            # Get the index
            self.segment_index = self.client.index(settings.meilisearch.segment_index)
            
            # Verify connection by getting index stats
            stats = self.segment_index.get_stats()
            logger.info(f"Connected to Meilisearch Cloud index: {stats.get('numberOfDocuments', 0)} documents indexed")
            
        except Exception as e:
            logger.error(f"Failed to connect to Meilisearch Cloud: {e}")
            raise

    def search_similar_segments(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for segments similar to the query text using Meilisearch semantic search."""
        try:
            # Perform semantic search with hybrid configuration
            search_results = self.segment_index.search(
                query,
                {
                    "limit": limit,
                    "showRankingScore": True,
                    "hybrid": {
                        "semanticRatio": 0.8,  # 80% semantic, 20% keyword matching
                        "embedder": "openai"  # Must match the embedder name in your cloud settings
                    },
                    "attributesToRetrieve": [
                        "id",
                        "video_id",
                        "text",
                        "start_time",
                        "end_time",
                        "speaker_id",
                        "metadata"
                    ]
                }
            )
            
            # Convert results to expected format
            segments = []
            for hit in search_results.get("hits", []):
                score = hit.get("_rankingScore", 0)
                if score >= threshold:
                    segments.append({
                        "id": hit["id"],
                        "video_id": hit["video_id"],
                        "text": hit["text"],
                        "start_time": float(hit["start_time"]),
                        "end_time": float(hit["end_time"]),
                        "speaker_id": hit.get("speaker_id"),
                        "similarity": score
                    })
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to search similar segments: {e}")
            return []

    def update_segment_embedding(self, segment_id: int, text: str) -> bool:
        """Update segment in Meilisearch index."""
        try:
            # Get full segment data from database
            segment = self.db.query(Segment).filter(Segment.id == segment_id).first()
            if not segment:
                return False
                
            # Prepare document for Meilisearch
            document = {
                "id": segment.id,
                "video_id": segment.video_id,
                "text": text,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "speaker_id": segment.speaker_id,
                "metadata": segment.segment_metadata
            }
            
            # Add or update document in Meilisearch
            self.segment_index.add_documents([document])
            return True
            
        except Exception as e:
            logger.error(f"Failed to update segment embedding: {e}")
            return False

    def batch_update_embeddings(self, segment_ids: List[int]) -> bool:
        """Update multiple segments in Meilisearch index."""
        try:
            # Get segments from database
            segments = (
                self.db.query(Segment)
                .filter(Segment.id.in_(segment_ids))
                .all()
            )
            
            # Prepare documents for Meilisearch
            documents = [{
                "id": segment.id,
                "video_id": segment.video_id,
                "text": segment.text,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "speaker_id": segment.speaker_id,
                "metadata": segment.segment_metadata
            } for segment in segments]
            
            # Add or update documents in Meilisearch
            if documents:
                self.segment_index.add_documents(documents)
            return True
            
        except Exception as e:
            logger.error(f"Failed to batch update embeddings: {e}")
            return False 