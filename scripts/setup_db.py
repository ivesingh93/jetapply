"""
Database setup script.
Run this once to create all database tables.

Usage:
    python scripts/setup_db.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, engine
from src.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database tables."""
    logger.info("Starting database setup...")
    
    try:
        # Test database connection
        with engine.connect() as conn:
            logger.info(f"✓ Successfully connected to database")
        
        # Create tables
        init_db()
        logger.info("✓ Database setup complete!")
        
        # Show created tables
        logger.info(f"Created tables: {', '.join(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error(f"✗ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()