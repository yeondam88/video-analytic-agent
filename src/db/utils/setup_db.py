import asyncio
from pathlib import Path
from loguru import logger

from src.db.database import db


async def setup_database():
    """Set up the database schema"""
    try:
        # Read the schema file
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r") as f:
            schema = f.read()

        # Split the schema into individual statements
        statements = [s.strip() for s in schema.split(";") if s.strip()]

        # Execute each statement
        for statement in statements:
            try:
                logger.info(f"Executing: {statement[:100]}...")  # Log first 100 chars
                await db.client.rpc('exec_sql', {'sql': statement}).execute()
            except Exception as e:
                logger.error(f"Failed to execute statement: {e}")
                raise

        logger.info("Database schema setup completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


async def create_exec_function():
    """Create a function to execute SQL statements"""
    try:
        # Create a function to execute SQL
        query = """
        CREATE OR REPLACE FUNCTION exec_sql(sql text)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            EXECUTE sql;
        END;
        $$;
        """
        
        await db.client.rpc('exec_sql', {'sql': query}).execute()
        logger.info("Created SQL execution function")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create SQL execution function: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(setup_database()) 