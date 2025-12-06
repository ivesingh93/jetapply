"""
Reset database by dropping and recreating all tables.
USE WITH CAUTION - This deletes all data!
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import drop_all_tables, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
    
    if response.lower() == 'yes':
        drop_all_tables()
        init_db()
        logger.info("✓ Database reset complete!")
    else:
        logger.info("Cancelled.")

if __name__ == "__main__":
    main()