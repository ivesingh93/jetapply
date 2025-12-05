from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
from contextlib import contextmanager
from typing import Generator
import logging

from src.config import settings
from src.models import Base

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10,
)

# Add connection pool listener for debugging
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    logger.debug("Database connection established")

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def init_db() -> None:
    """
    Initialize database by creating all tables.
    Call this once when setting up the project.
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_all_tables() -> None:
    """
    Drop all tables. Use with caution!
    Only for development/testing.
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")

def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Automatically handles commit/rollback and cleanup.
    
    Usage:
        with get_db() as db:
            job = db.query(Job).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session for manual management.
    Remember to close the session when done!
    
    Usage:
        db = get_db_session()
        try:
            job = db.query(Job).first()
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()
