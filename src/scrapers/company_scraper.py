import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.vectorstore.chroma_store import ChromaStore
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_and_store_company_page(
    company_name: str,
    base_url: str = None,
    store=None
) -> tuple[int, str]:
    """
    Scrape and store a company's about page.
    
    Args:
        company_name: Name of the company
        base_url: Base URL (optional, will auto-detect)
        store: ChromaStore instance
        
    Returns:
        Tuple of (chunks_stored, message)
    """
    if store is None:
        from src.vectorstore.chroma_store import ChromaStore
        store = ChromaStore()
    
    # Try to construct URLs if not provided
    if base_url is None:
        company_lower = company_name.lower().replace(" ", "")
        potential_urls = [
            f"https://www.{company_lower}.com",
            f"https://{company_lower}.com",
            f"https://{company_lower}.io",
        ]
    else:
        potential_urls = [base_url]
    
    # Try different about page patterns
    chunks = None
    successful_url = None
    
    for base in potential_urls:
        about_urls = [
            f"{base.rstrip('/')}/about",
            f"{base.rstrip('/')}/about-us",
            f"{base.rstrip('/')}/company",
            base
        ]
        
        for url in about_urls:
            try:
                chunks = scrape_and_chunk(url, company_name)
                if chunks and len(chunks) >= 3:
                    successful_url = url
                    break
            except Exception:
                continue
        
        if chunks:
            break
    
    if not chunks:
        return 0, f"❌ Could not scrape company page for {company_name}"
    
    # Store chunks
    stored_count = 0
    for chunk in chunks:
        try:
            doc_id = store.add_company_chunk(chunk["text"], chunk["metadata"])
            if doc_id:
                stored_count += 1
        except Exception as e:
            logger.error(f"Failed to store chunk: {e}")
    
    return stored_count, f"✓ Stored {stored_count} chunks from {successful_url}"

def scrape_and_chunk(url: str, company_name: str) -> list:
    """
    Scrape using Jina AI Reader - returns clean markdown.
    
    Jina AI automatically:
    - Removes navigation, ads, footers
    - Extracts main content
    - Returns clean markdown
    - No API key needed!
    
    Args:
        url: Page URL to scrape
        company_name: Name of the company
        
    Returns:
        List of chunks with metadata
    """
    # Jina AI Reader API - prepend r.jina.ai to any URL
    jina_url = f"https://r.jina.ai/{url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    response = requests.get(jina_url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Jina returns clean markdown text
    content = response.text
    
    # Validate content quality
    if len(content) < 500:
        raise Exception(f"Insufficient content: {len(content)} chars")
    
    logger.info(f"✓ Jina AI extracted {len(content):,} characters")
    
    # Use RecursiveCharacterTextSplitter (LangChain recommendation)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunk_texts = text_splitter.split_text(content)
    logger.info(f"✓ Created {len(chunk_texts)} semantic chunks")
    
    # Add metadata
    chunks = []
    for i, chunk_text in enumerate(chunk_texts):
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "company_name": company_name,
                "page_type": "about",
                "source_url": url,
                "section_title": f"Chunk {i+1}/{len(chunk_texts)}",
                "scraped_at": datetime.now().isoformat(),
                "chunk_index": i,
                "extraction_method": "jina_ai"
            }
        })
    
    return chunks