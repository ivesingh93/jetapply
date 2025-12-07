from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, UniqueConstraint
from sqlalchemy.sql import func

# ==================== Pydantic Models (for LangChain) ====================

class LocationType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"

class JobMetadata(BaseModel):
    """
    Pydantic model for structured metadata extraction.
    """
    location_type: LocationType = Field(
        description="Whether job is remote, hybrid, onsite, or unknown"
    )
    location: Optional[str] = Field(
        description="City and state/country if onsite or hybrid (e.g., 'San Francisco, CA')"
    )
    salary_min: Optional[float] = Field(
        description="Minimum salary for the job in USD"
    )
    salary_max: Optional[float] = Field(
        description="Maximum salary for the job in USD"
    )
    experience_years: Optional[int] = Field(
        description="Required years of experience for the job"
    )

# ==================== SQLAlchemy Models (for Database) ====================

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Job identifiers
    job_url = Column(String(500), nullable=False, unique=True, index=True)
    source = Column(String(100), nullable=False)  # e.g., "greenhouse", "lever"
    company_name = Column(String(200), nullable=False, index=True)
    
    # Job details
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Extracted metadata (from LLM)
    location_type = Column(String(50))  # remote/hybrid/onsite
    location = Column(String(200))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    experience_years = Column(Integer)
    
    # Tracking
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    embedded = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<Job(id={self.id}, company='{self.company_name}', title='{self.title}')>"