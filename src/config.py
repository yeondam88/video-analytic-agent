from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class APISettings(BaseModel):
    cors_origin_list: List[str] = ["*"]
    port: int = 8000
    host: str = "0.0.0.0"

class DatabaseSettings(BaseModel):
    url: str = "postgresql://postgres:postgres@localhost:5432/video_analytics"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

class OpenAISettings(BaseModel):
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.3

class DeepgramSettings(BaseModel):
    api_key: str
    model: str = "nova-2"
    tier: str = "enhanced"

class MeilisearchSettings(BaseModel):
    host: str = "http://localhost:7700"  # Should be overridden by env var MEILISEARCH__HOST
    api_key: str = ""  # Should be overridden by env var MEILISEARCH__API_KEY
    video_index: str = "videos"
    segment_index: str = "segments"
    embeddings_index: str = "embeddings"
    max_total_hits: int = 100
    search_limit: int = 20
    # Settings for the embedder that should match your cloud configuration
    embedder: dict = {
        "openai": {
            "source": "openAi",  # Note the capital A in openAi
            "dimensions": 1536,
            "model": "text-embedding-3-small",
            "documentTemplate": "{text}"
        }
    }
    # Additional settings for search configuration
    searchable_attributes: List[str] = ["text", "title"]
    filterable_attributes: List[str] = ["video_id", "speaker_id"]
    sortable_attributes: List[str] = ["start_time", "end_time"]
    ranking_rules: List[str] = [
        "words",
        "typo",
        "proximity",
        "attribute",
        "sort",
        "exactness",
        "_semanticScore"
    ]

class Settings(BaseSettings):
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    openai: OpenAISettings
    deepgram: DeepgramSettings
    meilisearch: MeilisearchSettings = MeilisearchSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings() 