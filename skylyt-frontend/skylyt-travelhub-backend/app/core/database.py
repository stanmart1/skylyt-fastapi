from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine with proper connection handling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1 hour
    pool_timeout=30,  # 30 seconds
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
    connect_args={
        "connect_timeout": 10,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "application_name": "skylyt_api"
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

# Connection event handlers for diagnostics
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    logger.info(f"New database connection established: {id(dbapi_connection)}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug(f"Connection checked out: {id(dbapi_connection)}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    logger.debug(f"Connection checked in: {id(dbapi_connection)}")

@event.listens_for(engine, "close")
def receive_close(dbapi_connection, connection_record):
    logger.info(f"Connection closed: {id(dbapi_connection)}")

@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    logger.error(f"Connection invalidated: {id(dbapi_connection)}, error: {exception}")

def get_db():
    db = SessionLocal()
    connection_id = id(db.connection())
    logger.debug(f"Creating database session: {connection_id}")
    try:
        yield db
        logger.debug(f"Database session completed successfully: {connection_id}")
    except Exception as e:
        logger.error(f"Database session error: {connection_id}, error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug(f"Database session closed: {connection_id}")