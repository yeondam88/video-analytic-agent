import os
import psycopg2
from dotenv import load_dotenv
from loguru import logger

def test_connection():
    """Test the database connection with the configured credentials."""
    # Load environment variables from .env
    load_dotenv()
    
    logger.info("Testing database connection...")
    
    try:
        # Get connection parameters
        host = os.getenv('SUPABASE_DB_HOST')
        port = os.getenv('SUPABASE_DB_PORT')
        user = os.getenv('SUPABASE_DB_USER')
        password = os.getenv('SUPABASE_DB_PASSWORD')
        database = os.getenv('SUPABASE_DB_NAME')
        
        logger.info(f"Connecting to database at {host}:{port}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            # For local development, we don't need SSL
            sslmode='disable' if host in ('localhost', '127.0.0.1') else 'require'
        )
        
        logger.info("Successfully connected to database")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        result = cur.fetchone()
        logger.info(f"Database Version: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    test_connection() 