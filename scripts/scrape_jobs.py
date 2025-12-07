import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


from src.scrapers import ScraperManager
from src.scrapers.agent_scraper import AgenticScraper
from src.database import get_db
from src.models import JobPosting
from src.config import settings

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

def save_jobs_to_db(raw_jobs: list) -> tuple[int, int]:
    """
    Save scraped jobs to database.
    
    Returns:
        Tuple of (new_count, duplicate_count)
    """
    new_count = 0
    duplicate_count = 0
    
    with get_db() as db:
        for raw_job in raw_jobs:
            # Check if job already exists (by URL)
            existing = db.query(JobPosting).filter_by(
                job_url=raw_job.job_url
            ).first()
            
            if existing:
                duplicate_count += 1
                logger.debug(f"Duplicate job: {raw_job.title} at {raw_job.company_name}")
                continue
            
            # Create new job posting
            job_posting = JobPosting(
                job_url=raw_job.job_url,
                source=raw_job.source,
                company_name=raw_job.company_name,
                title=raw_job.title,
                description=raw_job.description,
                location=raw_job.location,
                posted_date=raw_job.posted_date,
                scraped_at=datetime.now(),
            )
            
            db.add(job_posting)
            new_count += 1
            logger.debug(f"Added: {raw_job.title} at {raw_job.company_name}")
        
        db.commit()
    
    return new_count, duplicate_count

def main():
    parser = argparse.ArgumentParser(description="Scrape job postings from various sources")
    parser.add_argument(
        "--agentic",
        action="store_true",
        help="Use agentic scraper (auto-detects ATS)"
    )
    parser.add_argument(
        "--source", 
        choices=['greenhouse'],
        default='greenhouse',
        help="The source to scrape jobs from")

     # Company specification
    parser.add_argument(
        "--company",
        type=str,
        help="Company to scrape (agentic mode)"
    )
    parser.add_argument(
        "--companies",
        nargs="+",
        help="Multiple companies to scrape (agentic mode)"
    )
    
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Starting job scraping pipeline")
    logger.info("=" * 60)

    try:
        if args.agentic:
            agent = AgenticScraper()

            # Determine companies
            if args.company:
                companies = [args.company]
            elif args.companies:
                companies = args.companies
            else:
                companies = settings.COMPANIES_TO_SCRAPE
            
            logger.info(f"Scraping {len(companies)} companies with agent")

            # Scrape each company (agent saves to DB directly)
            total_new_jobs = 0
            for idx, company in enumerate(companies, 1):
                logger.info(f"\n[{idx}/{len(companies)}] 🤖 Agent scraping: {company}")
                
                try:
                    # Agent saves to DB, returns summary
                    jobs_count, summary = agent.scrape_company(company)
                    logger.info(f"  {summary}")
                    total_new_jobs += jobs_count
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed: {e}")
            
            # No need to call save_jobs_to_db() - already saved by tools!
            logger.info(f"\n{'=' * 60}")
            logger.info("Agentic scraping complete:")
            logger.info(f"  Companies: {len(companies)}")
            logger.info(f"  Total new jobs: {total_new_jobs}")
            logger.info(f"{'=' * 60}\n")
        else:
            manager = ScraperManager()
            raw_jobs = manager.scrape_source(args.source)
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Scraping complete: {len(raw_jobs)} jobs found")

            logger.info("Saving jobs to database...")
            new_count, duplicate_count = save_jobs_to_db(raw_jobs)

            logger.info(f"\n{'=' * 60}")
            logger.info("Database update complete:")
            logger.info(f"  - New jobs added: {new_count}")
            logger.info(f"  - Duplicates skipped: {duplicate_count}")
            logger.info(f"{'=' * 60}\n")

    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()