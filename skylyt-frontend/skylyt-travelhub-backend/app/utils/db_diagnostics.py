import logging
import time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from app.core.database import engine, SessionLocal

logger = logging.getLogger(__name__)

def check_db_connection():
    """Test database connectivity and log issues"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def execute_with_retry(query_func, max_retries=3):
    """Execute database query with retry logic"""
    for attempt in range(max_retries):
        try:
            return query_func()
        except (DisconnectionError, SQLAlchemyError) as e:
            logger.warning(f"Query attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Query failed after {max_retries} attempts")
                raise
            time.sleep(0.5 * (attempt + 1))

def log_query_execution(func):
    """Decorator to log query execution and catch null results"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if result is None:
                logger.warning(f"Query {func.__name__} returned None - possible connection issue")
            
            logger.debug(f"Query {func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper