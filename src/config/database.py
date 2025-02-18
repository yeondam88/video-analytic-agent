from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, field_validator, ConfigDict
from urllib.parse import quote_plus, urlencode

class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    
    model_config = ConfigDict(
        extra='allow',  # Allow extra fields
        env_file=".env",  # Read from .env file
        env_file_encoding="utf-8"  # Ensure proper encoding
    )
    
    # PostgreSQL settings
    DB_USER: str = Field("postgres", alias="SUPABASE_DB_USER")
    DB_PASSWORD: str = Field("postgres", alias="SUPABASE_DB_PASSWORD")
    DB_HOST: str = Field("localhost", alias="SUPABASE_DB_HOST")
    DB_PORT: int = Field(54322, alias="SUPABASE_DB_PORT")  # Default Supabase CLI port
    DB_NAME: str = Field("postgres", alias="SUPABASE_DB_NAME")
    
    # Connection pool settings
    DB_POOL_SIZE: int = Field(5, description="Database connection pool size")
    DB_POOL_TIMEOUT: int = Field(30, description="Database connection pool timeout")
    DB_MAX_OVERFLOW: int = Field(10, description="Maximum number of connections that can be created beyond pool_size")
    
    # The DATABASE_URL is built from the environment variables
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_db_url(cls, v: Optional[str], info):
        """Build the database URL from components."""
        if isinstance(v, str):
            return v
            
        # Get values from the validation context
        values = info.data
        
        user = values.get("DB_USER")
        password = values.get("DB_PASSWORD")
        host = values.get("DB_HOST")
        port = values.get("DB_PORT", 54322)  # Default Supabase CLI port
        name = values.get("DB_NAME", "").lstrip("/")  # Remove any leading slash
        
        if not all([user, password, host, name]):
            raise ValueError("Missing required database connection parameters")
            
        # Ensure proper escaping of special characters
        password = quote_plus(str(password))
        
        # For local development, we don't need sslmode=require
        is_local = host in ("localhost", "127.0.0.1")
        query_params = {"sslmode": "disable"} if is_local else {"sslmode": "require"}
        query_string = urlencode(query_params)
        
        # Build URL ensuring no double slashes in path
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}?{query_string}"
        return url
        
    def get_sqlalchemy_url(self) -> str:
        """Get the SQLAlchemy URL for database connection."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.build_db_url(None, self)
        return str(self.DATABASE_URL)

# For testing purposes
if __name__ == "__main__":
    settings = DatabaseSettings()
    print("Constructed DATABASE_URL:", settings.DATABASE_URL)