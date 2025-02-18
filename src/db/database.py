"""Database connection manager."""
import os
from typing import Optional, AsyncGenerator
from loguru import logger
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from urllib.parse import quote_plus, urlparse, parse_qs

from src.config import settings
from .models.base import Base

class Database:
    """Database connection manager."""
    _instance = None
    _client: Optional[Client] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[scoped_session] = None
    _async_engine = None
    _async_session = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the database singleton."""
        self._engine = None
        self._session_factory = None
        self._async_engine = None
        self._async_session_factory = None
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize database connections."""
        try:
            # Initialize Supabase client
            if not settings.services.SUPABASE_URL or not settings.services.SUPABASE_KEY:
                logger.warning("Supabase credentials not found")
                raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")

            self._client = create_client(
                settings.services.SUPABASE_URL,
                settings.services.SUPABASE_KEY
            )

            # Initialize SQLAlchemy engine
            db_url = settings.database.get_sqlalchemy_url()
            self._engine = create_engine(
                db_url,
                pool_size=settings.database.DB_POOL_SIZE,
                pool_timeout=settings.database.DB_POOL_TIMEOUT,
                max_overflow=settings.database.DB_MAX_OVERFLOW
            )

            # Create session factory
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )

            self._initialized = True
            logger.info("Successfully initialized database connections")

        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise

    @property
    def engine(self):
        """Get the SQLAlchemy engine."""
        return self._engine

    @engine.setter
    def engine(self, value):
        """Set the SQLAlchemy engine."""
        self._engine = value

    @property
    def session_factory(self):
        """Get the SQLAlchemy session factory."""
        return self._session_factory

    @session_factory.setter
    def session_factory(self, value):
        """Set the SQLAlchemy session factory."""
        self._session_factory = value

    @property
    def supabase(self):
        """Get the Supabase client."""
        return self._client

    @supabase.setter
    def supabase(self, value):
        """Set the Supabase client."""
        self._client = value

    def get_session(self):
        """Get a new database session."""
        if not self._session_factory:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self._async_session:
            raise RuntimeError("Async session not initialized")
        async with self._async_session() as session:
            yield session

    def close(self):
        """Close all database connections."""
        if self._session_factory:
            self._session_factory.remove()
        if self._engine:
            self._engine.dispose()
        if self._async_engine:
            self._async_engine.dispose()
        logger.info("Closed database connections")

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            # Test SQLAlchemy connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global database instance
db = Database()

# Session dependency
def get_db():
    """Get database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async for session in db.get_async_session():
        yield session 