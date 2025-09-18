from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
import logging
import time
import psutil
from app.core.config import settings

logger = logging.getLogger(__name__)

# Enhanced database engine with aggressive timeout handling
def get_connection_args():
    """Get database connection arguments based on database type"""
    if "postgresql" in settings.DATABASE_URL:
        return {
            "connect_timeout": 20,
            "keepalives_idle": 120,  # Reduced to 2 minutes for faster detection
            "keepalives_interval": 10,  # More frequent keepalives
            "keepalives_count": 3,  # Fewer retries before giving up
            "application_name": "skylyt_api",
            "sslmode": "disable",  # SSL disabled
            "options": "-c statement_timeout=30s -c idle_in_transaction_session_timeout=30s -c lock_timeout=15s"
        }
    return {}

# Adaptive pool sizing based on system resources
def get_pool_config():
    """Calculate optimal pool configuration based on system resources"""
    try:
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Increased pool size for higher concurrency
        base_pool_size = 100
        max_overflow = 50
        
        logger.info(f"Configured pool: size={base_pool_size}, overflow={max_overflow}")
        return base_pool_size, max_overflow
    except Exception as e:
        logger.warning(f"Failed to detect system resources: {e}, using defaults")
        return 100, 50

# Fixed pool configuration with logging
logger.info(f"Database URL: {settings.DATABASE_URL[:50]}...")
logger.info(f"Creating engine with pool_size=100, max_overflow=50")

# Remove any pool parameters from DATABASE_URL
clean_db_url = settings.DATABASE_URL.split('?')[0]
logger.info(f"Clean DB URL: {clean_db_url[:50]}...")

engine = create_engine(
    clean_db_url,
    pool_pre_ping=True,
    pool_recycle=300,  # 5 minutes
    pool_timeout=60,  # 60 seconds timeout
    pool_size=100,  # Fixed size
    max_overflow=50,  # Fixed overflow
    echo=False,
    poolclass=QueuePool,
    connect_args=get_connection_args(),
    execution_options={
        "autocommit": False,
        "isolation_level": "READ_COMMITTED"
    },
    pool_reset_on_return='commit'
)

# Log actual pool configuration after creation
logger.info(f"Engine created - Pool size: {engine.pool.size()}, Max overflow: {engine.pool._max_overflow}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database connection optimization
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@event.listens_for(engine, "connect")
def set_postgresql_search_path(dbapi_connection, connection_record):
    if "postgresql" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.close()

# Enhanced query performance monitoring with timeout detection
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()
    context._query_statement = statement[:500]  # Store more of the query

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    
    # Log different severity levels based on query time
    if total > 5.0:  # Critical - queries taking > 5 seconds
        logger.error(f"CRITICAL slow query ({total:.2f}s): {context._query_statement}")
    elif total > 2.0:  # Warning - queries taking > 2 seconds
        logger.warning(f"Slow query ({total:.2f}s): {context._query_statement}")
    elif total > 0.5:  # Info - queries taking > 500ms
        logger.info(f"Moderate query ({total:.2f}s): {statement[:100]}...")

# Enhanced connection recovery with retry logic
@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    logger.warning(f"Connection invalidated: {exception}")
    
    # Only dispose pool for truly critical errors, not server disconnections
    critical_errors = ["EOF", "connection reset", "broken pipe"]
    if any(error in str(exception).lower() for error in critical_errors):
        logger.error("Critical connection error detected, disposing entire pool")
        engine.dispose()
    elif "server closed the connection" in str(exception).lower():
        logger.info("Server closed connection - will reconnect automatically")
        # Let SQLAlchemy handle individual connection replacement



# Connection health monitoring
@event.listens_for(engine, "connect")
def set_connection_parameters(dbapi_connection, connection_record):
    """Set connection-level parameters for better timeout handling"""
    if "postgresql" in settings.DATABASE_URL:
        try:
            with dbapi_connection.cursor() as cursor:
                # Set connection-level timeouts
                cursor.execute("SET statement_timeout = '45s'")
                cursor.execute("SET lock_timeout = '30s'")
                cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
                cursor.execute("SET tcp_keepalives_idle = 300")
                cursor.execute("SET tcp_keepalives_interval = 15")
                cursor.execute("SET tcp_keepalives_count = 5")
        except Exception as e:
            logger.warning(f"Failed to set connection parameters: {e}")

# Pool status monitoring
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Monitor connection pool checkout"""
    pool = engine.pool
    
    # Only warn if pool is truly exhausted (95% utilization)
    total_capacity = pool.size() + pool.overflow()
    if pool.checkedout() > (total_capacity * 0.95):
        logger.warning(f"Pool utilization critical: {pool.checkedout()}/{total_capacity}")
    elif pool.checkedout() > (total_capacity * 0.9):
        logger.info(f"Pool utilization high: {pool.checkedout()}/{total_capacity}")

# Connection timeout recovery
@event.listens_for(engine, "handle_error")
def handle_error(exception_context):
    """Handle database errors with automatic recovery"""
    exception = exception_context.original_exception
    
    if "timeout" in str(exception).lower() or "connection" in str(exception).lower():
        logger.error(f"Database timeout/connection error: {exception}")
        # Force connection refresh on timeout
        if hasattr(exception_context, 'connection'):
            try:
                exception_context.connection.invalidate()
            except:
                pass

# Enhanced session management with timeout and SSL error handling
def get_db():
    """Database session with guaranteed cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as close_error:
            logger.warning(f"Session close error: {close_error}")

# Health check function for database connectivity
def check_database_health():
    """Check database connectivity and performance"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            db = SessionLocal()
            
            # Simple connectivity test
            result = db.execute(text("SELECT 1 as health_check"))
            row = result.fetchone()
            
            connection_time = time.time() - start_time
            
            db.close()
            
            return {
                "status": "healthy" if row and row[0] == 1 else "unhealthy",
                "connection_time": round(connection_time * 1000, 2),  # ms
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "attempt": attempt + 1
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle SSL errors with retry
            if "ssl connection has been closed unexpectedly" in error_msg and attempt < max_retries - 1:
                logger.warning(f"SSL error in health check (attempt {attempt + 1}): {e}")
                time.sleep(0.5)
                continue
            
            # Return error status
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_time": None,
                "attempt": attempt + 1
            }
    
    return {
        "status": "unhealthy",
        "error": "Max retry attempts exceeded",
        "connection_time": None,
        "attempt": max_retries
    }

# Connection pool management utilities
def reset_connection_pool():
    """Reset the connection pool in case of issues"""
    try:
        logger.info("Resetting database connection pool")
        engine.dispose()
        return True
    except Exception as e:
        logger.error(f"Failed to reset connection pool: {e}")
        return False

def get_pool_status():
    """Get detailed connection pool status"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_capacity": pool.size() + pool.overflow()
    }