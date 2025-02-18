from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel

class IVideoService(ABC):
    @abstractmethod
    async def process_video(self, url: str) -> Dict:
        """Process a video from the given URL."""
        pass

    @abstractmethod
    async def get_video(self, video_id: str) -> Optional[Dict]:
        """Retrieve video information by ID."""
        pass

    @abstractmethod
    async def list_videos(self) -> List[Dict]:
        """List all processed videos."""
        pass

class ISummaryService(ABC):
    @abstractmethod
    async def generate_summary(self, content: str) -> Dict:
        """Generate a summary from the given content."""
        pass

    @abstractmethod
    async def get_summary(self, video_id: str) -> Optional[Dict]:
        """Retrieve summary for a video."""
        pass

class IEmbeddingService(ABC):
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Create an embedding vector for the given text."""
        pass

    @abstractmethod
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar content using the query."""
        pass 