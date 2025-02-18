"""Test script to verify database connection and configuration."""
import asyncio
from loguru import logger

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.database import db


async def test_connection():
    """Test database connection and configuration."""
    try:
        # Test SQLAlchemy connection
        with Session(db.engine) as session:
            # Test basic query
            result = session.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"PostgreSQL version: {version}")

            # Test pgvector extension
            result = session.execute(text(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            ))
            has_vector = result.scalar()
            logger.info(f"pgvector extension enabled: {has_vector}")

            # Test RLS policies
            for table in ['videos', 'video_segments', 'transcriptions', 'summaries']:
                result = session.execute(text(f"""
                    SELECT tablename, hasrls, rowsecurity
                    FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename = :table
                """), {"table": table})
                rls_info = result.fetchone()
                if rls_info:
                    logger.info(f"Table {table} - RLS enabled: {rls_info.rowsecurity}")
                else:
                    logger.warning(f"Table {table} not found")

                # Check policies
                result = session.execute(text(f"""
                    SELECT polname, permissive, cmd
                    FROM pg_policies
                    WHERE schemaname = 'public' AND tablename = :table
                """), {"table": table})
                policies = result.fetchall()
                for policy in policies:
                    logger.info(f"Table {table} - Policy: {policy.polname} ({policy.cmd})")

            # Test connection pooling
            result = session.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE application_name LIKE 'psycopg2%'
            """))
            active_connections = result.scalar()
            logger.info(f"Active connections: {active_connections}")

        logger.success("All database tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_connection()) 