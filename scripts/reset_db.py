"""
Reset database by deleting the database file and recreating all tables.
USE WITH CAUTION - This deletes all data!
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
    
    if response.lower() == 'yes':
        # Extract database file path from DATABASE_URL
        # Format: "sqlite:///data/jobs.db"
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        db_file = Path(db_path)
        
        # Delete the database file if it exists
        if db_file.exists():
            logger.info(f"Deleting database file: {db_file}")
            db_file.unlink()
            logger.info("✓ Database file deleted")
        else:
            logger.info(f"Database file does not exist: {db_file}")
        
        # Recreate tables
        logger.info("Creating fresh database...")
        init_db()
        logger.info("✓ Database reset complete!")
    else:
        logger.info("Cancelled.")

if __name__ == "__main__":
    main()