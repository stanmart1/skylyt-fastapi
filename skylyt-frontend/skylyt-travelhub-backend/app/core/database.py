from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine with aggressive connection recovery
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # 5 minutes - much shorter
    pool_timeout=10,  # 10 seconds - fail fast
    pool_size=3,  # Minimal connections
    max_overflow=2,  # Max 5 total connections
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
        db.rollback()
        raise
    finally:
        db.close()