from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class RawJobPosting:
    """
    Raw job data from scraper before LLM processing.
    Maps directly to JobPosting model.
    """

    job_url: str
    source: str  # 'greenhouse', 'remoteok', etc.
    company_name: str
    title: str
    description: str
    requirements: Optional[str] = None
    posted_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.
        """
        data = asdict(self)
        data['posted_date'] = data['posted_date'].isoformat() if data['posted_date'] else None
        return data

class BaseScraper(ABC):
    """
    Base class for all job board scrapers.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"scraper.{source_name}")
    
    @abstractmethod
    def scrape_job_postings(self, **kwargs) -> List[RawJobPosting]:
        """
            Scrape jobs from the source.
        
            Returns:
                List of RawJobPosting objects
        """
        pass

    def validate_job_posting(self, job_posting: RawJobPosting) -> bool:
        """
        Validate that job has minimum required fields.
        """
        is_valid = bool(
            job_posting.job_url and
            job_posting.company_name and
            job_posting.title and
            job_posting.description and
            len(job_posting.description) > 50  # Minimum description length
        )
        
        if not is_valid:
            self.logger.warning(
                f"Invalid job: {job_posting.title} at {job_posting.company_name} - "
                f"URL: {bool(job_posting.job_url)}, Desc length: {len(job_posting.description or '')}"
            )
        
        return is_valid

    def get_headers(self) -> dict:
        """
        Common headers for HTTP requests
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
