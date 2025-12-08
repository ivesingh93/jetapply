# JetApply 🚀

An intelligent job scraping and search platform that autonomously discovers, extracts, and indexes job postings using AI agents and vector embeddings.

## ✨ Features

- **🤖 Agentic Scraping**: Autonomous job scraping using LangChain agents that automatically detect ATS systems
- **🔍 Smart Search**: Vector-based semantic search powered by ChromaDB and OpenAI embeddings
- **🔌 MCP Server**: Model Context Protocol server for AI assistants (Claude, etc.) to search jobs naturally
- **🏢 Multi-ATS Support**: Currently supports Greenhouse (more coming soon)
- **📊 Metadata Extraction**: AI-powered extraction of location type, salary, experience requirements
- **💾 Persistent Storage**: SQLite database with SQLAlchemy ORM

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone and install
git clone <repository-url>
cd jetapply
uv sync

# Create .env file with API keys
echo "OPENAI_API_KEY=your_openai_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_key" >> .env

# Setup database
uv run python scripts/setup_db.py
```

## 📖 Usage

### Scrape Jobs

```bash
# Agentic scraping (recommended) - automatically finds careers pages
uv run python scripts/scrape_jobs.py --agentic --company airbnb

# Scrape multiple companies
uv run python scripts/scrape_jobs.py --agentic --companies gitlab robinhood stripe
```

### Extract Metadata & Embed Jobs

```bash
# Extract metadata (location, salary, experience) and create embeddings
uv run python scripts/process_jobs.py
```

### Search Jobs

```bash
# Interactive semantic search
uv run python scripts/search_jobs.py
```

## 🔌 MCP Server

Connect AI assistants like Claude to search your job database using natural language.

**Setup:** Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "jetapply": {
      "command": "uv",
      "args": ["--directory", "/path/to/jetapply", "run", "python", "-m", "src.mcp.server"],
      "env": {
        "OPENAI_API_KEY": "your_openai_key_here"
      }
    }
  }
}
```

**Usage:** Ask Claude questions like:
- "Search for remote Python backend engineer jobs"
- "Find machine learning roles with 3+ years experience"
- "Show me onsite jobs in San Francisco"

## 🏗️ Architecture

```
jetapply/
├── src/
│   ├── scrapers/          # Agentic & ATS-specific scrapers
│   ├── extractors/        # AI-powered metadata extraction
│   ├── vectorstore/       # ChromaDB vector search
│   ├── mcp/              # MCP server for AI assistants
│   ├── models.py         # Data models
│   ├── database.py       # DB setup
│   └── config.py         # Configuration
├── scripts/              # CLI tools
└── data/                # SQLite & ChromaDB storage
```

## ⚙️ Configuration

Set in `.env` or `src/config.py`:

```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
ANTHROPIC_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=sqlite:///data/jobs.db
```

## 📊 Key Technologies

- **LangChain**: Agent orchestration
- **Anthropic Claude**: AI reasoning & extraction
- **OpenAI**: Text embeddings
- **ChromaDB**: Vector search
- **SQLAlchemy**: Database ORM
- **FastMCP**: MCP server framework

## 🛠️ Scripts

| Script | Purpose |
|--------|---------|
| `scrape_jobs.py` | Scrape jobs (agentic or traditional) |
| `process_jobs.py` | Extract metadata & create embeddings |
| `search_jobs.py` | Semantic job search |
| `setup_db.py` | Initialize database |

## 🎯 Roadmap

- [ ] Lever & Workday ATS support
- [ ] Periodic scraping scheduler
- [ ] Web UI for job search
- [ ] Job application tracking
- [ ] Email notifications