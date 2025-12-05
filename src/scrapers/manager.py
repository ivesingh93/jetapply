from typing import List, Dict
from .base import BaseScraper, RawJobPosting
from .greenhouse import GreenhouseScraper
import logging

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manages all job scrapers and provides a unified interface.
    """
    def __init__(self):
        self.scrapers: Dict[str, BaseScraper] = {
            'greenhouse': GreenhouseScraper(),
        }
    def scrape_source(self, source: str, **kwargs) -> List[RawJobPosting]:
        """
        Run a specific scraper with custom arguments.
        
        Args:
            source: Source name ('greenhouse' or 'remoteok')
            **kwargs: Additional arguments to pass to the scraper
        
        Returns:
            List of RawJobPosting objects
        """
        if source not in self.scrapers:
            raise ValueError(f"Unknown scraper source: {source}")
        
        scraper = self.scrapers[source]
        return scraper.scrape_job_postings(**kwargs)