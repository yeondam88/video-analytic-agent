from typing import List, Dict, Any, Optional
from meilisearch import Client
from loguru import logger
from sqlalchemy.orm import Session
import openai
from datetime import datetime
import numpy as np
from pgvector.sqlalchemy import Vector

from src.config import settings
from src.db.models.video import Video
from src.db.models.segment import Segment
from src.api.database import db  # Import the global db instance
from src.api.services.embedding_service import EmbeddingService

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
        self.client = Client(settings.meilisearch.host, settings.meilisearch.api_key)
        
        # Configure indices for basic search
        try:
            # Create indices if they don't exist
            self.client.create_index(settings.meilisearch.video_index, {"primaryKey": "id"})
            self.client.create_index(settings.meilisearch.segment_index, {"primaryKey": "id"})
            
            # Configure video index
            self.client.index(settings.meilisearch.video_index).update_settings({
                "searchableAttributes": ["title", "description", "text"],
                "filterableAttributes": ["source", "status", "created_at"],
                "sortableAttributes": ["created_at"]
            })
            
            # Configure segment index
            self.client.index(settings.meilisearch.segment_index).update_settings({
                "searchableAttributes": ["text", "display_text", "title"],
                "filterableAttributes": ["video_id", "speaker_id", "created_at"],
                "sortableAttributes": ["start_time", "created_at"]
            })
            
            logger.info("Successfully configured Meilisearch indices")
        except Exception as e:
            logger.error(f"Failed to configure indices: {e}")

    def search_videos(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Basic search using Meilisearch."""
        try:
            search_params = {
                "limit": limit,
                "attributesToRetrieve": ["*"],
                "attributesToHighlight": ["text", "title"],
                "cropLength": 200
            }
            
            if filters:
                filter_expressions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        filter_expressions.extend([f"{key} = '{v}'" for v in value])
                    else:
                        filter_expressions.append(f"{key} = '{value}'")
                search_params["filter"] = filter_expressions
                logger.debug(f"Search filters: {filter_expressions}")
            
            # Search in video index
            results = self.client.index(settings.meilisearch.video_index).search(
                query,
                search_params
            )
            
            # Log search results for debugging
            logger.debug(f"Raw search results: {results}")
            logger.info(f"Search query '{query}' returned {len(results['hits']) if 'hits' in results else 0} results")
            
            # Return hits or empty list
            return results.get('hits', [])
            
        except Exception as e:
            logger.error(f"Failed to search videos: {e}")
            raise

    def index_video(self, video: Video) -> None:
        """Index a video in Meilisearch."""
        try:
            # Convert model to dictionary and ensure all values are JSON serializable
            video_doc = {
                "id": str(video.id),
                "url": str(video.url),
                "title": str(video.title) if video.title else None,
                "description": str(video.description) if video.description else None,
                "duration": float(video.duration) if video.duration else None,
                "status": str(video.status.value) if video.status else None,
                "thumbnail_url": str(video.thumbnail_url) if video.thumbnail_url else None,
                "progress": float(video.progress) if video.progress else 0.0,
                "steps_completed": video.steps_completed or [],
                "error": str(video.error) if video.error else None,
                "created_at": video.created_at.isoformat() if video.created_at else None,
                "updated_at": video.updated_at.isoformat() if video.updated_at else None,
                "source": str(video.source.value) if video.source else None,
                "metadata": {
                    k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                    for k, v in (video.metadata or {}).items()
                }
            }
            
            self.client.index(settings.meilisearch.video_index).add_documents([video_doc])
            logger.info(f"Indexed video {video.id} in Meilisearch")
            
        except Exception as e:
            logger.error(f"Failed to index video {video.id} in Meilisearch: {e}")
            raise

    def index_segment(self, segment: Segment) -> None:
        """Index a video segment in Meilisearch with embeddings."""
        try:
            # Generate embeddings for the segment text
            response = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=segment.text,
                encoding_format="float"
            )
            embedding = response.data[0].embedding
            
            # Convert embedding to pgvector type and update segment
            segment.embedding = embedding
            self.db.commit()
            
            # Index in Meilisearch for keyword search
            segment_doc = {
                "id": str(segment.id),
                "video_id": str(segment.video_id),
                "text": str(segment.text),
                "start_time": float(segment.start_time) if segment.start_time else None,
                "end_time": float(segment.end_time) if segment.end_time else None,
                "speaker_id": str(segment.speaker_id) if segment.speaker_id else None,
                "display_text": str(segment.display_text) if segment.display_text else None,
                "title": str(segment.title) if segment.title else None,
                "metadata": {
                    k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                    for k, v in (segment.segment_metadata or {}).items()
                },
                "created_at": segment.created_at.isoformat() if segment.created_at else None,
                "updated_at": segment.updated_at.isoformat() if segment.updated_at else None
            }
            
            self.client.index(settings.meilisearch.segment_index).add_documents([segment_doc])
            logger.info(f"Indexed segment {segment.id} in Meilisearch")
            
        except Exception as e:
            logger.error(f"Failed to index segment {segment.id}: {e}")
            raise

    def search_segments(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for segments using semantic search."""
        try:
            return self.embedding_service.search_similar_segments(
                query=query,
                limit=limit,
                threshold=threshold
            )
        except Exception as e:
            logger.error(f"Failed to search segments: {e}")
            return []

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Semantic search for segments."""
        return self.search_segments(query, limit, threshold)

    def search_video_segments(
        self,
        video_id: int,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for segments within a specific video."""
        try:
            # Get all similar segments
            segments = self.search_segments(query, limit=limit * 2, threshold=threshold)
            
            # Filter for the specific video and respect the original limit
            video_segments = [
                segment for segment in segments
                if segment["video_id"] == video_id
            ][:limit]
            
            return video_segments
            
        except Exception as e:
            logger.error(f"Failed to search video segments: {e}")
            return []

    async def reindex_all(self):
        """Reindex all videos and segments in Meilisearch."""
        try:
            # Get all videos
            videos = self.db.query(Video).all()
            
            # Prepare video documents
            video_docs = []
            for video in videos:
                # Convert metadata to dict if it's not already
                metadata = {}
                if hasattr(video, 'metadata') and video.metadata:
                    try:
                        if isinstance(video.metadata, dict):
                            metadata = video.metadata
                        else:
                            metadata = dict(video.metadata)
                    except:
                        metadata = {}
                
                # Convert all non-serializable values to strings
                metadata = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                    for k, v in metadata.items()
                }
                
                doc = {
                    "id": str(video.id),
                    "url": str(video.url),
                    "title": str(video.title) if video.title else None,
                    "description": str(video.description) if video.description else None,
                    "duration": float(video.duration) if video.duration else None,
                    "status": str(video.status.value) if video.status else None,
                    "source": str(video.source.value) if video.source else None,
                    "thumbnail_url": str(video.thumbnail_url) if video.thumbnail_url else None,
                    "progress": float(video.progress) if video.progress else 0.0,
                    "steps_completed": video.steps_completed or [],
                    "error": str(video.error) if video.error else None,
                    "created_at": video.created_at.isoformat() if video.created_at else None,
                    "updated_at": video.updated_at.isoformat() if video.updated_at else None,
                    "metadata": metadata
                }
                video_docs.append(doc)
            
            # Clear and reindex videos
            self.client.index(settings.meilisearch.video_index).delete_all_documents()
            if video_docs:
                self.client.index(settings.meilisearch.video_index).add_documents(video_docs)
            
            logger.info(f"Successfully reindexed {len(video_docs)} videos")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reindex documents: {e}")
            raise 