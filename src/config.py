from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    #API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    #Anthropic
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4000

    #Embedding Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    BATCH_SIZE: int = 50

    #Database Settings
    DATABASE_URL: str = "sqlite:///data/jobs.db"
    CHROMA_DB_NAME: str = "jetapply"
    CHROMA_COLLECTION_NAME: str = "job_postings"

    #Scraping Settings
    SCRAPE_INTERVAL_HOURS: int = 6
    COMPANIES_TO_SCRAPE: list[str] = ['airbnb']
    JOB_KEYWORDS: list[str] = [
        'Software Engineer', 
        'Senior Software Engineer',
        'Software Developer',
        'Data Engineer', 
        'Machine Learning Engineer', 
        'AI Engineer', 
        'ML Engineer',
        'Java Developer',
        'Python Developer',
        'Full Stack Developer',
        'Backend Developer',
        'Scala Developer',
    ]

settings = Settings()