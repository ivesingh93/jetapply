"""JetApply MCP Server - Semantic job search using ChromaDB."""
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vectorstore.chroma_store import ChromaStore
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("jetapply")


@mcp.tool()
async def search_jobs(
    query: str,
    location_type: Optional[str] = None,
    limit: int = 5
) -> str:
    """Search for jobs using AI-powered semantic search.
    
    Args:
        query: Natural language job search query (e.g., 'Python backend engineer with kubernetes')
        location_type: Filter by location type: 'remote', 'hybrid', or 'onsite'
        limit: Maximum number of results to return (default: 5)
    """
    try:
        # Lazy load ChromaStore
        store = ChromaStore()
        
        # Build filters
        filters = {}
        if location_type and location_type in ["remote", "hybrid", "onsite"]:
            filters["location_type"] = location_type
        
        # Search using ChromaDB
        results = store.search(
            query=query,
            filter_dict=filters if filters else None,
            k=limit
        )
        
        if not results:
            return "No jobs found matching your criteria."
        
        # Format results
        output = f"🔍 Found {len(results)} relevant jobs:\n\n"
        for i, job in enumerate(results, 1):
            output += f"{i}. **{job.get('title', 'N/A')}** at {job.get('company_name', 'N/A')}\n"
            output += f"   📍 {job.get('location_type', 'N/A')}"
            if job.get('location'):
                output += f" - {job['location']}"
            output += "\n"
            
            if job.get('salary_min') and job.get('salary_max'):
                output += f"   💰 ${job['salary_min']:,} - ${job['salary_max']:,}\n"
            
            if job.get('experience_years'):
                output += f"   📊 {job['experience_years']} years experience\n"
            
            output += f"   🔗 {job.get('job_url', 'N/A')}\n"
            
            if 'similarity' in job:
                output += f"   📊 Relevance: {job['similarity']:.1%}\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"""❌ Error searching jobs: {str(e)}

Make sure:
1. OPENAI_API_KEY is set in .env file
2. ChromaDB is initialized with job data
3. Jobs have been embedded in the database

Run 'uv run python scripts/process_jobs.py' to embed jobs if needed."""

def main():
    """Run the MCP server."""
    # Run with stdio transport
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()