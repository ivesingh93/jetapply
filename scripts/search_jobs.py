"""
Semantic search for jobs in ChromaDB.
Usage: 
    python scripts/search_jobs.py "Python developer"
    python scripts/search_jobs.py "Machine Learning Engineer" --limit 10
    python scripts/search_jobs.py "remote backend engineer" --location-type remote
"""
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore import ChromaStore

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings/errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def display_results(results: list[dict]):
    """Display search results in a nice format."""
    if not results:
        print("\n❌ No results found.\n")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Found {len(results)} matching jobs")
    print(f"{'=' * 80}\n")
    
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result['title']}")
        print(f"   Company: {result['company']}")
        print(f"   Location: {result['location_type']}" + (f" - {result['location']}" if result['location'] else ""))
        print(f"   Salary: {result['salary_range']}")
        print(f"   Experience: {result['experience_years']} years")
        print(f"   Relevance: {result['relevance']} (distance: {result['distance']:.4f}, similarity: {result['score']:.2%})")
        print(f"   Job ID: {result['job_id']}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description="Semantic search for jobs in ChromaDB"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (natural language)"
    )
    parser.add_argument(
        "-k", "--limit",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "--location-type",
        choices=["remote", "hybrid", "onsite"],
        help="Filter by location type"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show ChromaDB statistics"
    )
    args = parser.parse_args()

    try:
        store = ChromaStore()
    except Exception as e:
        print(f"Failed to initialize ChromaDB: {e}")
        sys.exit(1)

    # Show stats if requested
    if args.stats:
        stats = store.get_stats()
        print("\n" + "=" * 80)
        print("ChromaDB Statistics")
        print("=" * 80)
        print(f"Collection: {stats.get('collection_name')}")
        print(f"Total Jobs: {stats.get('total_documents')}")
        print(f"Location: {stats.get('persist_directory')}")
        print()
        if not args.query:
            return

    # Build filter
    filter_dict = None
    if args.location_type:
        filter_dict = {"location_type": args.location_type}

    # Perform search
    print(f"\n🔍 Searching for: '{args.query}'")
    if filter_dict:
        print(f"   Filters: {filter_dict}")
    
    results = store.search(args.query, k=args.limit, filter_dict=filter_dict)
    
    # Display results
    display_results(results)


if __name__ == "__main__":
    main()