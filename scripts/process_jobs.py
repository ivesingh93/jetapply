import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_db
from src.models import JobPosting
from src.extractors import MetadataExtractor
from src.vectorstore import ChromaStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

def process_jobs(limit: Optional[int]) -> tuple[int, int]:
    """
    Process jobs: extract metadata and create embeddings.

    Returns:
        Tuple of (metadata_count, embedding_count, error_count)
    """
    extractor = MetadataExtractor()
    chroma_store = ChromaStore()

    embedding_count = 0
    error_count = 0

    with get_db() as db:
        # Query jobs that need processing
        query = db.query(JobPosting)

        # Process jobs that need either metadata or embeddings
        query = query.filter(JobPosting.embedded == False)

        if limit:
            query = query.limit(limit)
        
        jobs = query.all()
        total = len(jobs)
        logger.info(f"Found {total} jobs to process")

        for idx, job in enumerate(jobs, 1):
            logger.info(f"\nProcessing job {idx}/{total}: {job.id} - {job.title}")

            try:
                # Extract metadata and create embeddings if needed
                metadata = extractor.extract(job)
                if metadata:
                    doc_id = chroma_store.add_job(job=job, metadata=metadata)

                    if doc_id:
                        embedding_count += 1
                        job.embedded = True
                        job.location_type = metadata.location_type.value if metadata.location_type else None
                        job.location = metadata.location
                        job.salary_min = int(metadata.salary_min) if metadata.salary_min else None
                        job.salary_max = int(metadata.salary_max) if metadata.salary_max else None
                        job.experience_years = metadata.experience_years
                    else:
                        error_count += 1
                        logger.warning(f"Failed to create embedding for job {job.id}")
                
                else:
                    error_count += 1
                    logger.warning(f"Failed to extract metadata for job {job.id}")
                    continue
                db.commit()
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing job {job.id}: {e}", exc_info=True)
                db.rollback()
                continue
    return embedding_count, error_count

def main():
    parser = argparse.ArgumentParser(
        description="Extract metadata and create embeddings for job postings"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of jobs to process"
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Starting job processing pipeline")
    logger.info("=" * 60)

    try:
        embedding_count, error_count = process_jobs(args.limit)
        
        logger.info(f"\n{'=' * 60}")
        logger.info("Processing complete:")
        logger.info(f"  ✓ Embeddings created: {embedding_count}")
        logger.info(f"  ✗ Errors: {error_count}")
        logger.info(f"{'=' * 60}\n")
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()