from typing import Optional, Any, Dict, List, TypeVar, Generic, AsyncGenerator
from functools import wraps
import time
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from supabase import create_client, Client
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from src.config import settings

T = TypeVar('T')

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass

class ConnectionError(DatabaseError):
    """Exception for connection errors."""
    pass

class QueryError(DatabaseError):
    """Exception for query errors."""
    pass

def with_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying database operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                        time.sleep(wait_time)
            raise last_error
        return wrapper
    return decorator

class Database:
    """Singleton database client that manages both Supabase and SQLAlchemy connections."""
    
    _instance: Optional['Database'] = None
    _supabase: Optional[Client] = None
    _engine = None
    _SessionLocal = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def _initialize(self):
        """Initialize database connections."""
        if self._initialized:
            return
            
        try:
            # Initialize Supabase client
            self._supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
                options={
                    'db_url': settings.get_sqlalchemy_url(),
                    'auth': {
                        'autoRefreshToken': True,
                        'persistSession': True
                    }
                }
            )
            
            # Initialize SQLAlchemy engine
            self._engine = create_engine(
                settings.get_sqlalchemy_url(),
                pool_pre_ping=True,         # Enable connection health checks
                pool_size=5,                # Set base pool size
                max_overflow=10,            # Allow up to 10 connections beyond pool_size
                pool_timeout=30,            # Connection timeout in seconds
                pool_recycle=1800,         # Recycle connections after 30 minutes
                connect_args={
                    "sslmode": "require",   # Force SSL
                    "connect_timeout": 10   # Connection attempt timeout
                }
            )
            
            # Create session factory
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            self._initialized = True
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise ConnectionError(f"Database initialization failed: {e}")
    
    @property
    def supabase(self) -> Client:
        """Get the Supabase client, initializing if necessary."""
        if not self._initialized:
            self._initialize()
        return self._supabase
    
    def get_session(self) -> Session:
        """Get a database session, initializing if necessary."""
        if not self._initialized:
            self._initialize()
        return self._SessionLocal()
    
    @with_retry()
    async def create(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new record."""
        try:
            if not self._initialized:
                self._initialize()
            response = await self.supabase.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create record in {table}: {e}")
            raise QueryError(f"Create operation failed: {e}")
    
    @with_retry()
    async def read(self, table: str, id: Any) -> Optional[Dict[str, Any]]:
        """Read a record by ID."""
        try:
            if not self._initialized:
                self._initialize()
            response = await self.supabase.table(table).select("*").eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to read record from {table}: {e}")
            raise QueryError(f"Read operation failed: {e}")
    
    @with_retry()
    async def update(self, table: str, id: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        try:
            if not self._initialized:
                self._initialize()
            response = await self.supabase.table(table).update(data).eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to update record in {table}: {e}")
            raise QueryError(f"Update operation failed: {e}")
    
    @with_retry()
    async def delete(self, table: str, id: Any) -> Optional[Dict[str, Any]]:
        """Delete a record by ID."""
        try:
            if not self._initialized:
                self._initialize()
            response = await self.supabase.table(table).delete().eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to delete record from {table}: {e}")
            raise QueryError(f"Delete operation failed: {e}")
    
    @with_retry()
    async def list(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List records with pagination."""
        try:
            if not self._initialized:
                self._initialize()
            response = await self.supabase.table(table).select("*").range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to list records from {table}: {e}")
            raise QueryError(f"List operation failed: {e}")

# Create database instance
db = Database()

# Create async engine
engine = create_async_engine(
    settings.database.get_sqlalchemy_url(),
    echo=False,
    future=True
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close() 