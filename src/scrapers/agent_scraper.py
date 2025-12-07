"""
Agentic scraper that autonomously decides how to scrape each company.
Uses LangChain agents with database-saving tools.
"""

import logging
import re
from typing import Tuple
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from src.config import settings
from src.scrapers.tools import (
    find_company_jobs_page,
    detect_ats_system,
    scrape_and_save_greenhouse_jobs
)

logger = logging.getLogger(__name__)

class AgenticScraper:
    """
    Autonomous scraper agent that saves jobs directly to database.
    Tools return compact summaries to avoid token limits.
    """
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0
        )
        
        # Define tools (they save to DB and return summaries)
        self.tools = [
            find_company_jobs_page,
            detect_ats_system,
            scrape_and_save_greenhouse_jobs
        ] 

        # Create agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt="""You are an autonomous job scraping agent.

Your tools SAVE jobs directly to the database and return summaries.

Available tools:
- find_company_jobs_page → returns URL
- detect_ats_system → returns "greenhouse", "lever", or "unknown"
- scrape_and_save_greenhouse_jobs → scrapes AND saves, returns summary

Strategy:
1. Find the careers page URL
2. Detect which ATS system is used
3. Extract company slug from URL (e.g., "airbnb" from "boards.greenhouse.io/airbnb")
4. Based on ATS:
   - "greenhouse" → use scrape_and_save_greenhouse_jobs
5. Return the summary message

Tools handle saving - you orchestrate the workflow."""
        )

        logger.info("AgenticScraper initialized with database-saving tools")
    def scrape_company(self, company_name: str) -> Tuple[int, str]:
        """
        Scrape jobs using agent (saves to DB directly).
        
        Args:
            company_name: Name of the company (e.g., "Netflix", "Airbnb")
            
        Returns:
            Tuple of (jobs_count, summary_message)
        """
        try:
            logger.info(f"🤖 Agent scraping: {company_name}")
            
            # Let the agent figure it out!
            result = self.agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Scrape and save all jobs from {company_name}"
                }]
            })
            
            # Extract summary from agent's final message
            final_message = result.get("messages", [])[-1].content if result.get("messages") else "No response"
            
            # Parse job count from summary - match multiple possible formats
            # Format 1: "Saved X new jobs" (from tool output)
            # Format 2: "**Jobs Saved**: X new jobs" (from agent summary)
            match = re.search(r'(?:Saved|Jobs Saved.*?)(\d+) new jobs', final_message)
            jobs_count = int(match.group(1)) if match else 0
            
            logger.info(f"✓ Agent completed: {final_message}")
            return jobs_count, final_message
            
        except Exception as e:
            logger.error(f"✗ Agent failed to scrape {company_name}: {e}", exc_info=True)
            return 0, f"Error: {str(e)}"