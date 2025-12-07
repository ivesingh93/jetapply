"""
Tools for the agentic scraper.
Each tool is a focused function the agent can call.
Tools save directly to database and return compact summaries.
"""
from langchain.tools import tool
import logging
import requests
from datetime import datetime
from src.database import get_db
from src.models import JobPosting

logger = logging.getLogger(__name__)

@tool
def find_company_jobs_page(company_name: str) -> str:
    """
    Find a company's jobs/careers page URL.
    
    Args:
        company_name: Company name (e.g., "Netflix", "Airbnb")
        
    Returns:
        URL string (compact)
    """
    try:
        company_slug = company_name.lower().replace(' ', '')
        
        # Prioritize ATS patterns
        common_patterns = [
            f"https://boards.greenhouse.io/{company_slug}",
            f"https://jobs.{company_slug}.com",
            f"https://{company_slug}.com/careers",
            f"https://careers.{company_slug}.com",
            f"https://www.{company_slug}.com/jobs"
        ]
        
        for url in common_patterns:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"✓ Found careers page: {url}")
                    return url
            except:
                continue
        
        logger.warning(f"✗ Could not find careers page for {company_name}")
        # Return best guess
        return f"https://boards.greenhouse.io/{company_slug}"
        
    except Exception as e:
        logger.error(f"Error finding jobs page: {e}")
        return f"https://{company_name.lower()}.com/careers"   

@tool
def detect_ats_system(url: str) -> str:
    """
    Detect which ATS (Applicant Tracking System) a careers page uses.
    
    Args:
        url: Careers page URL
        
    Returns:
        ATS name: "greenhouse" or "unknown"
    """
    try:
        url_lower = url.lower()
        
        # Check URL pattern first (most reliable)
        if 'greenhouse.io' in url_lower:
            logger.info(f"✓ Detected Greenhouse from URL")
            return "greenhouse"
        
        # Fetch page and check HTML markers
        response = requests.get(url, timeout=10, allow_redirects=True)
        html_lower = response.text.lower()
        
        # Check for ATS markers in HTML
        if 'greenhouse' in html_lower or 'boards-api.greenhouse' in html_lower:
            logger.info(f"✓ Detected Greenhouse from HTML")
            return "greenhouse"
        
        logger.warning(f"✗ Could not detect ATS system")
        return "unknown"
        
    except Exception as e:
        logger.error(f"Error detecting ATS: {e}")
        return "unknown"

@tool
def scrape_and_save_greenhouse_jobs(company_slug: str) -> str:
    """
    Scrape Greenhouse jobs and SAVE TO DATABASE.
    
    Args:
        company_slug: Company slug for Greenhouse (e.g., "airbnb", "netflix")
        
    Returns:
        Compact summary string (not full data)
    """
    try:
        # Use existing GreenhouseScraper
        from src.scrapers.greenhouse import GreenhouseScraper
        
        scraper = GreenhouseScraper()
        raw_jobs = scraper.scrape_company(company_slug)
        
        if not raw_jobs:
            return f"No jobs found from Greenhouse for {company_slug}"
        
        # Save to database immediately
        new_count = 0
        duplicate_count = 0
        
        with get_db() as db:
            for raw_job in raw_jobs:
                # Check if exists
                existing = db.query(JobPosting).filter_by(
                    job_url=raw_job.job_url
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Create new job
                job_posting = JobPosting(
                    job_url=raw_job.job_url,
                    source=raw_job.source,
                    company_name=raw_job.company_name,
                    title=raw_job.title,
                    description=raw_job.description,
                    location=raw_job.location,
                    posted_date=raw_job.posted_date,
                    scraped_at=datetime.now(),
                    embedded=False
                )
                
                db.add(job_posting)
                new_count += 1
            
            db.commit()
        
        # Return compact summary
        summary = f"✓ Saved {new_count} new jobs to database (from {len(raw_jobs)} total, {duplicate_count} duplicates)"
        logger.info(summary)
        return summary
        
    except Exception as e:
        error_msg = f"✗ Error scraping Greenhouse: {str(e)}"
        logger.error(error_msg)
        return error_msg