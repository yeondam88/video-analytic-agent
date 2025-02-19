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
    host: str = "http://localhost:7700"
    api_key: str = ""
    video_index: str = "videos"
    segment_index: str = "segments"
    embeddings_index: str = "embeddings"
    max_total_hits: int = 100
    search_limit: int = 20

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