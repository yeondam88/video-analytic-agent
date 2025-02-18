"""External services settings for the application."""
from typing import Optional
from pydantic import Field, model_validator

from .base import BaseAppSettings

class ExternalServicesSettings(BaseAppSettings):
    """Settings for external services."""
    
    # Supabase
    SUPABASE_URL: Optional[str] = Field(
        default=None,
        description="Supabase project URL"
    )
    SUPABASE_KEY: Optional[str] = Field(
        default=None,
        description="Supabase service role key"
    )
    
    # Deepgram
    DEEPGRAM_API_KEY: Optional[str] = Field(
        default=None,
        description="Deepgram API key for transcription"
    )
    DEEPGRAM_MODEL: str = Field(
        default="nova-2",
        description="Deepgram model to use for transcription"
    )
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI features"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="OpenAI model to use for text generation"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI model to use for embeddings"
    )
    
    @model_validator(mode='after')
    def validate_required_keys(self) -> 'ExternalServicesSettings':
        """Validate that required API keys are provided."""
        required_keys = {
            'Supabase URL': self.SUPABASE_URL,
            'Supabase Key': self.SUPABASE_KEY,
            'Deepgram API Key': self.DEEPGRAM_API_KEY,
            'OpenAI API Key': self.OPENAI_API_KEY
        }
        
        missing_keys = [k for k, v in required_keys.items() if not v]
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
            
        return self 