"""
Company Info RAG system - ask questions about companies.
Usage:
    python scripts/company_info_rag.py "What does Stripe do?"
    python scripts/company_info_rag.py "What is the company mission?" --company Stripe
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from src.intelligence import CompanyRAG

def main():
    parser = argparse.ArgumentParser(description="Ask questions about companies using RAG")
    parser.add_argument("question", help="Your question")
    parser.add_argument("--company", "-c", help="Filter by company name")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🤖 Company Intelligence RAG System")
    print("="*70)
    
    # Initialize RAG
    print("\nInitializing...", end=" ")
    rag = CompanyRAG()
    print("✓")
    
    # Process query
    print(f"\n💬 Question: {args.question}")
    if args.company:
        print(f"   Filter: {args.company}")
    
    print("\n🤔 Thinking...\n")
    
    # Get answer
    answer, sources = rag.query(args.question, company_name=args.company)
    
    # Display answer
    print("="*70)
    print("📝 Answer:")
    print("="*70)
    print(f"\n{answer}\n")
    
    # Display sources
    if sources:
        print("="*70)
        print(f"📚 Sources ({len(sources)} chunks used):")
        print("="*70)
        for i, source in enumerate(sources[:3], 1):  # Show top 3
            print(f"\n{i}. {source['company_name']} (Similarity: {source['similarity']:.1%})")
            print(f"   {source['source_url']}")
            print(f"   Preview: {source['content'][:150]}...")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()