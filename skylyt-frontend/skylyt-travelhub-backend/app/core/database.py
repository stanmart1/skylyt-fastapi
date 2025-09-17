from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
import time
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine with production-ready connection pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # 5 minutes
    pool_timeout=60,  # 60 seconds timeout
    pool_size=25,  # Base connections
    max_overflow=15,  # Max 40 total connections
    echo=False,
    connect_args={
        "connect_timeout": 5,
        "keepalives_idle": 600,  # 10 minutes
        "keepalives_interval": 30,
        "keepalives_count": 3,
        "application_name": "skylyt_api",
        "sslmode": "prefer"  # Handle SSL issues gracefully
    } if "postgresql" in settings.DATABASE_URL else {}
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

# Query performance monitoring
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log queries taking > 1 second
        logger.warning(f"Slow query ({total:.2f}s): {statement[:200]}...")

# Aggressive connection recovery
@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    logger.error(f"Connection invalidated, disposing pool: {exception}")
    # Force immediate pool disposal on SSL errors
    if "SSL" in str(exception) or "EOF" in str(exception):
        engine.dispose()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        try:
            db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        raise
    finally:
        try:
            db.close()
        except Exception:
            pass  # Ignore close errors