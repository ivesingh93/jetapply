"""
Development utility to inspect ChromaDB contents.
Usage: python tools/test_chroma.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore import ChromaStore

def main():
    # Initialize ChromaStore
    store = ChromaStore()

    # Get the collection directly
    collection = store.vectorstore._collection

    # Check basic stats
    print("=" * 60)
    print("ChromaDB Collection Stats")
    print("=" * 60)
    print(f"Collection name: {collection.name}")
    print(f"Total documents: {collection.count()}")
    print()

    # Get all documents (limit 10)
    results = collection.get(limit=10, include=['documents', 'metadatas'])

    print("=" * 60)
    print("Stored Jobs:")
    print("=" * 60)

    for idx, (doc_id, doc, metadata) in enumerate(zip(
        results['ids'], 
        results['documents'], 
        results['metadatas']
    ), 1):
        print(f"\n{idx}. Job ID: {metadata.get('job_id')}")
        print(f"   Title: {metadata.get('title')}")
        print(f"   Company: {metadata.get('company_name')}")
        print(f"   Location: {metadata.get('location_type')} - {metadata.get('location')}")
        print(f"   Salary: {metadata.get('salary_min')} - {metadata.get('salary_max')}")
        print(f"   Experience: {metadata.get('experience_years')} years")
        print(f"   ChromaDB ID: {doc_id}")

if __name__ == "__main__":
    main()