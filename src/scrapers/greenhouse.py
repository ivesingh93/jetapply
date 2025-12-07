from typing import List, Optional
import requests
from datetime import datetime
from .base import BaseScraper, RawJobPosting
import time

class GreenhouseScraper(BaseScraper):
    """
    Scraper for Greenhouse ATS.

    Greenhouse provides a public API for job postings.
    https://boards-api.greenhouse.io/v1/boards/{company}/jobs
    """

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    def __init__(self):
        super().__init__("greenhouse")

    def scrape_job_postings(
        self, 
        companies: Optional[List[str]] = None,
        delay: float = 5.0, 
        **kwargs
    ) -> List[RawJobPosting]:

        """
        Scrape jobs from Greenhouse for specified companies.
        
        Args:
            companies: List of company slugs (e.g., ['airbnb', 'stripe'])
                      If None, uses COMPANIES_TO_SCRAPE from config
            delay: Delay between requests in seconds (be polite!)
        
        Returns:
            List of RawJobPosting objects
        """
        if companies is None:
            from src.config import settings
            companies = settings.COMPANIES_TO_SCRAPE
        
        self.logger.info(f"Starting Greenhouse scrape for {len(companies)} companies")

        all_job_postings = []
        failed_companies = []

        for i, company in enumerate(companies, 1):
            self.logger.info(f"[{i}/{len(companies)}] Scraping {company}...")

            try:
                job_postings = self.scrape_company(company)
                all_job_postings.extend(job_postings)
                self.logger.info(f"✓ Found {len(job_postings)} jobs for {company}")

                if i < len(companies):
                    time.sleep(delay)
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.logger.warning(f"✗ Company '{company}' not found on Greenhouse")
                else:
                    self.logger.error(f"✗ HTTP error for {company}: {e}")
                failed_companies.append(company)
            except Exception as e:
                self.logger.error(f"✗ Failed to scrape {company}: {e}")
                failed_companies.append(company)

        self.logger.info(
            f"Greenhouse scrape complete: {len(all_job_postings)} jobs from "
            f"{len(companies) - len(failed_companies)}/{len(companies)} companies"
        )

        if failed_companies:
            self.logger.warning(f"Failed companies: {', '.join(failed_companies)}")
        
        return all_job_postings
    
    def scrape_company(self, company_slug: str) -> List[RawJobPosting]:
        """
        Scrape all jobs for a single company
        """
        url = self.BASE_URL.format(company=company_slug)

        response = requests.get(
            url,
            headers=self.get_headers(),
            params={'content': 'true'},
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        jobs = []

        for job_data in data.get('jobs', []):
            job = self.parse_job_posting(job_data, company_slug)
            if job and self.validate_job_posting(job):
                jobs.append(job)

        return jobs
    
    def parse_job_posting(self, job_data: dict, company_slug: str) -> Optional[RawJobPosting]:
        """
        Parse Greenhouse API response into RawJobPosting
        """
        try:
            # Parse posted/updated date
            posted_date = None
            if job_data.get('updated_at'):
                try:
                    # Greenhouse uses ISO format with 'Z' for UTC
                    date_str = job_data['updated_at'].replace('Z', '+00:00')
                    posted_date = datetime.fromisoformat(date_str)
                except (ValueError, AttributeError) as e:
                    self.logger.debug(f"Could not parse date: {e}")
            
            location_info = job_data.get('location', {})
            location_text = location_info.get('name', '') if isinstance(location_info, dict) else str(location_info)

            # Build full description
            description_parts = []
            if job_data.get('content'):
                description_parts.append(job_data['content'])
            
            if job_data.get('title'):
                description_parts.append(f"\n\nJob Title: {job_data['title']}")
            
            description = '\n'.join(description_parts)

            return RawJobPosting(
                job_url=job_data.get('absolute_url', ''),
                source='greenhouse',
                company_name=company_slug,
                title=job_data.get('title', ''),
                location=location_text or None,
                description=description,
                posted_date=posted_date,
            )
        except KeyError as e:
            self.logger.error(f"Missing required field in job data: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing job: {e}")
            return None