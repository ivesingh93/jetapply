from typing import List, Dict
from .base import BaseScraper, RawJobPosting
from .greenhouse import GreenhouseScraper
from src.scrapers.agent_scraper import AgenticScraper
import logging

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manages all job scrapers and provides a unified interface.
    """
    def __init__(self):
        self.scrapers: Dict[str, BaseScraper] = {
            'greenhouse': GreenhouseScraper(),
            'agent': AgenticScraper()
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

        if source == 'agent':
            # Agentic mode - requires company name
            company = kwargs.get('company')
            if not company:
                raise ValueError("Agentic mode requires --company argument")
            return [scraper.scrape_company(company)]
        else:
            # Traditional mode
            return scraper.scrape_job_postings(**kwargs)