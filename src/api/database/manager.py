"""Database manager for handling connections and queries."""
import time
from typing import Optional, Any, Dict, List, Generator
from functools import wraps
import asyncio
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from fastapi import Depends
from urllib.parse import urlparse, parse_qs

from src.config import settings
from src.db.models.base import Base

class DatabaseError(Exception):
    """Base class for database exceptions."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when database query fails."""
    pass

def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0, exponential: bool = True):
    """Decorator for retrying database operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential: Whether to use exponential backoff
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (SQLAlchemyError, OperationalError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = min(
                            base_delay * (2 ** attempt if exponential else 1),
                            max_delay
                        )
                        logger.warning(
                            f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                except Exception as e:
                    # Don't retry on non-database errors
                    logger.error(f"Non-database error occurred: {e}")
                    raise
            
            raise last_error
        return wrapper
    return decorator

class DatabaseManager:
    """Database manager for handling connections and queries."""
    
    _instance: Optional['DatabaseManager'] = None
    _supabase: Optional[Client] = None
    _engine = None
    _session_factory = None
    _initialized = False
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the database manager."""
        if not self._initialized:
            self._initialize()
    
    def _initialize(self):
        """Initialize database connections."""
        try:
            # Initialize Supabase client
            if not settings.services.SUPABASE_URL or not settings.services.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")
            
            self._supabase = create_client(
                settings.services.SUPABASE_URL,
                settings.services.SUPABASE_KEY
            )
            
            # Initialize SQLAlchemy engine
            self._engine = create_engine(
                settings.database.get_sqlalchemy_url(),
                pool_pre_ping=True,
                pool_size=settings.database.DB_POOL_SIZE,
                max_overflow=settings.database.DB_MAX_OVERFLOW,
                pool_timeout=settings.database.DB_POOL_TIMEOUT
            )
            
            # Create session factory
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise ConnectionError(f"Database initialization failed: {e}")
    
    @property
    def supabase(self) -> Client:
        """Get Supabase client."""
        if not self._supabase:
            raise ConnectionError("Supabase client not initialized")
        return self._supabase
    
    @property
    def client(self) -> Client:
        """Alias for supabase property."""
        return self.supabase
    
    def get_session(self):
        """Get database session."""
        if not self._session_factory:
            raise ConnectionError("Session factory not initialized")
        return self._session_factory()
    
    @with_retry()
    async def create(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        try:
            response = self.supabase.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise QueryError(f"Failed to create record: {e}")
    
    @with_retry()
    async def read(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Read a record by ID."""
        try:
            response = self.supabase.table(table).select("*").eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise QueryError(f"Failed to read record: {e}")
    
    @with_retry()
    async def update(self, table: str, id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        try:
            response = self.supabase.table(table).update(data).eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise QueryError(f"Failed to update record: {e}")
    
    @with_retry()
    async def delete(self, table: str, id: int) -> bool:
        """Delete a record by ID."""
        try:
            response = self.supabase.table(table).delete().eq("id", id).execute()
            return bool(response.data)
        except Exception as e:
            raise QueryError(f"Failed to delete record: {e}")
    
    @with_retry()
    async def list(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List records with pagination."""
        try:
            response = self.supabase.table(table).select("*").range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            raise QueryError(f"Failed to list records: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self.get_session()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            logger.error(f"Error in database session: {exc_val}")
            raise exc_type(exc_val)

# Global database instance
db = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close() 