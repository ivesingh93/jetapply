# JetApply 🚀

An intelligent job scraping and search platform that autonomously discovers, extracts, and indexes job postings using AI agents and vector embeddings.

## ✨ Features

- **🤖 Agentic Scraping**: Autonomous job scraping using LangChain agents that automatically detect ATS systems
- **🔍 Smart Search**: Vector-based semantic search powered by ChromaDB and OpenAI embeddings
- **🏢 Multi-ATS Support**: Currently supports Greenhouse (more coming soon)
- **📊 Metadata Extraction**: AI-powered extraction of location type, salary, experience requirements
- **💾 Persistent Storage**: SQLite database with SQLAlchemy ORM
- **🔄 Duplicate Prevention**: Automatic detection and skipping of existing job postings

## 🏗️ Architecture

```
jetapply/
├── src/
│   ├── scrapers/          # Scraping logic
│   │   ├── agent_scraper.py    # Agentic autonomous scraper
│   │   ├── greenhouse.py       # Greenhouse ATS scraper
│   │   ├── tools.py           # LangChain tools for agents
│   │   └── manager.py         # Scraper orchestration
│   ├── extractors/        # Metadata extraction
│   │   └── metadata_extractor.py
│   ├── vectorstore/       # Vector search
│   │   └── chroma_store.py
│   ├── models.py          # Pydantic & SQLAlchemy models
│   ├── database.py        # Database connection & setup
│   └── config.py          # Configuration management
├── scripts/               # CLI scripts
│   ├── scrape_jobs.py    # Main scraping script
│   ├── process_jobs.py   # Metadata extraction
│   ├── search_jobs.py    # Vector search
│   └── setup_db.py       # Database initialization
├── notebooks/            # Jupyter notebooks for exploration
└── data/                 # SQLite database storage
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd jetapply
```

2. Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

3. Install dependencies:
```bash
uv sync
```

4. Setup the database:
```bash
uv run python scripts/setup_db.py
```

## 📖 Usage

### Agentic Scraping (Recommended)

The agentic scraper autonomously finds careers pages, detects ATS systems, and saves jobs:

```bash
# Scrape a single company
uv run python scripts/scrape_jobs.py --agentic --company airbnb

# Scrape multiple companies
uv run python scripts/scrape_jobs.py --agentic --companies gitlab robinhood stripe

# Use default companies from config
uv run python scripts/scrape_jobs.py --agentic
```

**How it works:**
1. Agent finds the company's careers page
2. Detects which ATS system they use (Greenhouse, Lever, etc.)
3. Scrapes all job postings
4. Saves directly to database, avoiding duplicates

### Traditional Scraping

```bash
# Scrape from Greenhouse (default companies in config)
uv run python scripts/scrape_jobs.py --source greenhouse
```

### Extract Metadata

Process scraped jobs to extract structured metadata (location type, salary, experience):

```bash
uv run python scripts/process_jobs.py
```

### Search Jobs

Semantic search using vector embeddings:

```bash
uv run python scripts/search_jobs.py
```

## ⚙️ Configuration

Edit `src/config.py` or set environment variables:

```python
# API Keys (required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Models
ANTHROPIC_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=text-embedding-3-small

# Database
DATABASE_URL=sqlite:///data/jobs.db
CHROMA_DB_PATH=./chroma_db

# Scraping
COMPANIES_TO_SCRAPE=['airbnb', 'gitlab', 'stripe']
JOB_KEYWORDS=['Software Engineer', 'Data Engineer', ...]
```

## 📊 Database Schema

### JobPosting Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| job_url | String | Unique job posting URL |
| source | String | ATS system (greenhouse, lever) |
| company_name | String | Company name |
| title | String | Job title |
| description | Text | Full job description |
| location_type | String | remote/hybrid/onsite |
| location | String | City, State/Country |
| salary_min/max | Integer | Salary range in USD |
| experience_years | Integer | Required years of experience |
| posted_date | DateTime | When job was posted |
| scraped_at | DateTime | When we scraped it |
| embedded | Boolean | Vector embedding status |

## 🛠️ Scripts Reference

| Script | Description |
|--------|-------------|
| `scrape_jobs.py` | Main scraping interface (agentic or traditional) |
| `process_jobs.py` | Extract metadata from job descriptions |
| `search_jobs.py` | Semantic search interface |
| `setup_db.py` | Initialize database schema |
| `reset_db.py` | Reset database (⚠️ destructive) |

## 🧪 Development

### Run Jupyter Notebooks

```bash
uv run jupyter notebook
```

Explore the notebooks:
- `01_greenhouse_jobs.ipynb` - Greenhouse scraping exploration
- `02_parse_jobs.ipynb` - Metadata extraction experiments
- `03_store_jobs.ipynb` - Vector storage examples

### Project Dependencies

Key libraries:
- **LangChain**: Agent orchestration and LLM integration
- **Anthropic Claude**: AI agent and metadata extraction
- **OpenAI**: Text embeddings for semantic search
- **ChromaDB**: Vector database for job search
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and settings

## 💡 Examples

### Example 1: Scrape GitLab Jobs

```bash
uv run python scripts/scrape_jobs.py --agentic --company gitlab
```

**Output:**
```
🤖 Agent scraping: gitlab
✓ Found careers page: https://boards.greenhouse.io/gitlab
✓ Detected Greenhouse from URL
✓ Saved 115 new jobs to database (from 115 total, 0 duplicates)

Agentic scraping complete:
  Companies: 1
  Total new jobs: 115
```

### Example 2: Scrape Multiple Companies

```bash
uv run python scripts/scrape_jobs.py --agentic --companies airbnb robinhood gitlab
```

**Output:**
```
[1/3] 🤖 Agent scraping: airbnb
✓ Saved 186 new jobs to database

[2/3] 🤖 Agent scraping: robinhood
✓ Saved 96 new jobs to database

[3/3] 🤖 Agent scraping: gitlab
✓ Saved 115 new jobs to database

Total new jobs: 397
```

### Example 3: Extract Metadata from Jobs

```bash
uv run python scripts/process_jobs.py
```

**Extracts:**
- Location type (remote/hybrid/onsite)
- Salary ranges
- Experience requirements
- Office locations

### Example 4: Search for Remote ML Jobs

```bash
uv run python scripts/search_jobs.py "machine learning engineer with python" --location-type remote --limit 10
```

**Output:**
```
🔍 Searching for: 'machine learning engineer with python'
   Filters: {'location_type': 'remote'}

================================================================================
Found 10 matching jobs
================================================================================

1. Senior Machine Learning Engineer
   Company: Airbnb
   Location: remote
   Salary: $150,000 - $200,000
   Experience: 5 years
   Relevance: High (distance: 0.2341, similarity: 88%)
   Job ID: 123

2. ML Engineer - Python
   Company: GitLab
   Location: remote
   Salary: $140,000 - $180,000
   Experience: 3 years
   Relevance: High (distance: 0.2567, similarity: 85%)
   Job ID: 456
...
```

**View ChromaDB stats:**
```bash
uv run python scripts/search_jobs.py --stats
```

## 🎯 Roadmap

- [ ] Add support for Lever ATS
- [ ] Add support for Workday ATS
- [ ] Implement periodic scraping scheduler
- [ ] Add more sophisticated search filters
- [ ] Build web UI for job search
- [ ] Add job application tracking
- [ ] Email notifications for new matching jobs


