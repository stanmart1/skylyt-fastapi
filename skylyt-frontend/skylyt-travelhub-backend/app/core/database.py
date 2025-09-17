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
            "connect_timeout": 15,  # Increased from 5
            "keepalives_idle": 300,  # Reduced from 600 (5 minutes)
            "keepalives_interval": 15,  # Reduced from 30
            "keepalives_count": 5,  # Increased from 3
            "application_name": "skylyt_api",
            "sslmode": "prefer",
            "options": "-c statement_timeout=45s -c idle_in_transaction_session_timeout=60s -c lock_timeout=30s"
        }
    return {}

# Adaptive pool sizing based on system resources
def get_pool_config():
    """Calculate optimal pool configuration based on system resources"""
    try:
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Base pool size on CPU cores and available memory
        base_pool_size = max(20, min(cpu_count * 4, 50))
        max_overflow = max(15, min(cpu_count * 2, 30))
        
        logger.info(f"Configured pool: size={base_pool_size}, overflow={max_overflow}")
        return base_pool_size, max_overflow
    except Exception as e:
        logger.warning(f"Failed to detect system resources: {e}, using defaults")
        return 30, 20

pool_size, max_overflow = get_pool_config()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,  # 30 minutes instead of 5
    pool_timeout=180,  # 3 minutes timeout (increased from 60s)
    pool_size=pool_size,  # Dynamic sizing
    max_overflow=max_overflow,  # Dynamic overflow
    echo=False,
    poolclass=QueuePool,
    connect_args=get_connection_args(),
    # Add engine-level timeouts
    execution_options={
        "autocommit": False,
        "isolation_level": "READ_COMMITTED"
    }
)

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
    logger.error(f"Connection invalidated: {exception}")
    
    # Immediate pool disposal for specific errors
    critical_errors = ["SSL", "EOF", "timeout", "connection reset", "broken pipe"]
    if any(error in str(exception).lower() for error in critical_errors):
        logger.error("Critical connection error detected, disposing entire pool")
        engine.dispose()

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
    logger.debug(f"Pool status - Size: {pool.size()}, Checked out: {pool.checkedout()}, "
                f"Overflow: {pool.overflow()}")
    
    # Warn if pool is getting full
    if pool.checkedout() > (pool.size() * 0.8):
        logger.warning(f"Pool utilization high: {pool.checkedout()}/{pool.size() + pool.overflow()}")

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

# Enhanced session management with timeout handling
def get_db():
    """Enhanced database session with timeout and error handling"""
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Test connection immediately
        db.execute(text("SELECT 1"))
        yield db
        
    except Exception as e:
        session_duration = time.time() - start_time
        logger.error(f"Database session error after {session_duration:.2f}s: {e}")
        
        # Handle specific timeout errors
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            logger.error("Database timeout detected, invalidating connection")
            try:
                db.invalidate()
            except:
                pass
        
        # Attempt rollback with timeout protection
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.warning(f"Rollback failed: {rollback_error}")
        
        raise
        
    finally:
        session_duration = time.time() - start_time
        
        # Log long-running sessions
        if session_duration > 30:
            logger.warning(f"Long database session: {session_duration:.2f}s")
        
        # Safe session cleanup
        try:
            db.close()
        except Exception as close_error:
            logger.warning(f"Session close error: {close_error}")

# Health check function for database connectivity
def check_database_health():
    """Check database connectivity and performance"""
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
            "overflow": engine.pool.overflow()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection_time": None
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