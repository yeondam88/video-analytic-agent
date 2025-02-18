from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

class ServicesSettings(BaseSettings):
    """External services configuration."""
    
    model_config = ConfigDict(
        extra='allow',  # Allow extra fields
        env_file=None,  # Don't read from .env file in tests
        case_sensitive=True,  # Case sensitive environment variables
        env_prefix="",  # No prefix for environment variables
        env_file_encoding="utf-8"  # Ensure proper encoding
    )
    
    # Supabase
    SUPABASE_URL: str = Field(
        default="http://localhost:54321",
        env="SUPABASE_URL",
        description="Supabase project URL"
    )
    SUPABASE_KEY: Optional[str] = Field(
        default=None,
        env="SUPABASE_KEY",
        description="Supabase service role key"
    )
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY",
        description="OpenAI API key for AI features"
    )
    
    # Deepgram
    DEEPGRAM_API_KEY: Optional[str] = Field(
        default=None,
        env="DEEPGRAM_API_KEY",
        description="Deepgram API key for transcription"
    )
    
    # Feature flags
    ENABLE_VECTOR_SEARCH: bool = Field(
        default=True,
        env="ENABLE_VECTOR_SEARCH",
        description="Enable vector search functionality"
    )
    ENABLE_DIARIZATION: bool = Field(
        default=True,
        env="ENABLE_DIARIZATION",
        description="Enable speaker diarization"
    )
    ENABLE_SUMMARIES: bool = Field(
        default=True,
        env="ENABLE_SUMMARIES",
        description="Enable content summarization"
    ) 