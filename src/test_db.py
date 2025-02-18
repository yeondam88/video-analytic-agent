import os
from dotenv import load_dotenv
from loguru import logger
import psycopg2

def test_db():
    """Test database connection."""
    # Load environment variables
    load_dotenv()
    
    # Get Deepgram API key
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    logger.info(f"Deepgram API key: {'Present' if deepgram_key else 'Missing'}")
    
    # Get database credentials
    db_host = os.getenv('SUPABASE_DB_HOST', 'localhost')
    db_port = os.getenv('SUPABASE_DB_PORT', '5432')
    db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
    db_pass = os.getenv('SUPABASE_DB_PASSWORD', 'postgres')
    db_name = os.getenv('SUPABASE_DB_NAME', 'video_analytics')
    
    logger.info(f"Database settings:")
    logger.info(f"Host: {db_host}")
    logger.info(f"Port: {db_port}")
    logger.info(f"User: {db_user}")
    logger.info(f"Database: {db_name}")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database=db_name,
            sslmode='disable' if db_host in ('localhost', '127.0.0.1') else 'require'
        )
        
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()
            logger.info(f"Connected to PostgreSQL version: {version[0]}")
            
            # Test if we can create a table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Successfully created test table")
            
            # Clean up
            cur.execute("DROP TABLE test_connection;")
            conn.commit()
            logger.info("Successfully cleaned up test table")
            
        logger.success("Database connection test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    test_db() 