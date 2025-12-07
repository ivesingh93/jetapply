from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from src.models import JobMetadata, JobPosting
from src.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """
    Extract structured metadata from job postings using LangChain LCEL.
    """

    def __init__(self):
        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from job postings.

            Extract the following metadata from the job posting:

            - location_type: remote, hybrid, onsite, or unknown
            - location: City and state/country if onsite or hybrid
            - salary_min: number or null
            - salary_max: number or null
            - experience_years: Required years of experience

            If information is not available, use null/None for optional fields."""),
            ("human", """Job Title: {title}

            Job Description:
            {description}
            """)
        ])

        # Create model with structured output
        model = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS
        )
        structured_model = model.with_structured_output(JobMetadata)

        # Compose chain
        self.chain = self.prompt | structured_model

        logger.info("MetadataExtractor initialized")

    def extract(self, job: JobPosting) -> Optional[JobMetadata]:
        """
        Extract metadata from a job posting.

        Args:
            job: JobPosting instance

        Returns:
            JobMetadata instance or None if extraction fails
        """

        try:
            # Invoke the chain
            result = self.chain.invoke({
                "title": job.title,
                "description": job.description
            })
            logger.info(f"Extracted metadata for job {job.id}: {job.title}")
            return result
        except Exception as e:
            logger.error(f"Failed to extract metadata for job {job.id}: {e}", exc_info=True)
            return None

