import logging

from src.models import JobMetadata, JobPosting
from src.config import settings
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import Optional
import hashlib
logger = logging.getLogger(__name__)

class ChromaStore:
    """
    Wrapper around LangChain's Chroma vector store.
    """

    def __init__(self):
        # Ensure directory exists
        persist_dir = Path(settings.CHROMA_DB_PATH)
        persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings (ChromaDB will use this automatically)
        embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Initialize Chroma vector store
        self.vectorstore = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(persist_dir)
        )

        logger.info(f"ChromaStore initialized at {persist_dir}")
    
    def add_job(
        self,
        job: JobPosting,
        metadata: JobMetadata
    ) -> Optional[str]:

        """
        Add a job posting to ChromaDB.
        Embeddings are created automatically by ChromaDB.
        
        Args:
            job_id: Database job ID
            title: Job title
            description: Job description
            metadata: Additional metadata dict
            
        Returns:
            Document ID in ChromaDB or None if failed
        """

        try:
            # Combine title and description for the doc
            document_text = f"{job.title} \n\n{job.description}"

            # Add more fields to metadata
            full_metadata = {
                "company_name": job.company_name,
                "job_id": str(job.id),
                "title": job.title,
                "location_type": metadata.location_type.value if metadata.location_type else "",
                "location": metadata.location or "",
                "salary_min": str(metadata.salary_min) if metadata.salary_min else "",
                "salary_max": str(metadata.salary_max) if metadata.salary_max else "",
                "experience_years": str(metadata.experience_years) if metadata.experience_years else ""
            }

            # Add vectorstore
            doc_ids = self.vectorstore.add_texts(
                texts=[document_text],
                metadatas=[full_metadata],
                ids=[f"job_{job.id}"]
            )

            logger.info(f"Added job {job.id} to ChromaDB")
            return doc_ids[0] if doc_ids else None
        except Exception as e:
            logger.error(f"✗ Failed to add job {job.id} to ChromaDB: {e}", exc_info=True)
            return None

    def add_company_chunk(self, text: str, metadata: dict) -> Optional[str]:
        """
        Add a company information chunk to ChromaDB.
        
        Args:
            text: The chunk content
            metadata: Dict with company_name, page_type, source_url, section_title, scraped_at
            
        Returns:
            Document ID or None if failed
        """
        try:
            # Generate unique ID from company name and text snippet
            chunk_id = hashlib.md5(
                f"{metadata['company_name']}_{text[:50]}".encode()
            ).hexdigest()

            # Add to vectorstore
            doc_ids = self.vectorstore.add_texts(
                texts=[text],
                metadatas=[metadata],
                ids=[f"company_{chunk_id}"]
            )

            logger.info(f"Added company chunk for {metadata['company_name']}")
            return doc_ids[0] if doc_ids else None
        except Exception as e:
            logger.error(f"Failed to add company chunk: {e}")
            return None
    
    def search_companies(
        self,
        query: str,
        company_name: Optional[str] = None,
        k: int = 5
    ) -> list:
        """
        Search company information chunks.
        
        Args:
            query: Natural language query
            company_name: Optional filter by specific company
            k: Number of results
            
        Returns:
            List of matching chunks with metadata
        """

        try:
            # Build filter if company specific
            filter_dict = None
            if company_name:
                filter_dict = {"company_name": company_name}

            # Search
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=filter_dict
            )

            chunks = []
            for doc, distance in results:
                similarity = max(0, 1 - distance)
                chunks.append({
                    "content": doc.page_content,
                    "company_name": doc.metadata.get("company_name", ""),
                    "page_type": doc.metadata.get("page_type", ""),
                    "source_url": doc.metadata.get("source_url", ""),
                    "section_title": doc.metadata.get("section_title", ""),
                    "similarity": float(similarity)
                })
            logger.info(f"Found {len(chunks)} company chunks for: '{query}'")
            return chunks
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def company_exists(self, company_name: str) -> bool:
        """
        Check if a company already has data in the vector store.
        
        Args:
            company_name: Company name to check
            
        Returns:
            True if company has at least one chunk stored
        """
        try:
            # Search for any chunk from this company
            results = self.vectorstore.similarity_search(
                query="",  # Empty query, just filter by metadata
                k=1,
                filter={"company_name": company_name}
            )
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error checking if company exists: {e}")
            return False  # Assume doesn't exist on error, will try to scrape

    def search(self, query: str, k: int = 5, filter_dict: Optional[dict] = None) -> list[dict]:
        """
        Semantic search for similar jobs

        Args:
            query: Natural language search query
            k: Number of results to return
            filter_dict: Optional metadata filters (e.g. {"location_type": "remote"})
        """
        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=filter_dict
            )

            job_results = []
            for doc, distance in results:
                # Convert distance to similarity score (0-1, higher = better)
                # Typical distances are 0.2-2.0, so we normalize
                similarity_score = max(0, 1 - distance)  # Invert: lower distance = higher similarity
                job_results.append({
                    "job_id": int(doc.metadata.get("job_id", 0)),
                    "title": doc.metadata.get("title", ""),
                    "company": doc.metadata.get("company_name", ""),
                    "source": doc.metadata.get("source", ""),
                    "location_type": doc.metadata.get("location_type", ""),
                    "location": doc.metadata.get("location", ""),
                    "salary_range": f"{doc.metadata.get('salary_min', 'N/A')} - {doc.metadata.get('salary_max', 'N/A')}",
                    "experience_years": doc.metadata.get("experience_years", "N/A"),
                    "content": doc.page_content,
                    "distance": float(distance),
                    "score": float(similarity_score),
                    "relevance": "High" if distance < 0.4 else "Medium" if distance < 0.8 else "Low"
                })
            
            logger.info(f"Found {len(job_results)} results for query: '{query}'")
            return job_results
        except Exception as e:
            logger.error(f"✗ Failed to search ChromaDB: {e}", exc_info=True)
            return []

    def get_stats(self) -> dict:
        """
        Get statistics about the ChromaDB collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            # Access the underlying Chroma collection
            collection = self.vectorstore._collection
            
            return {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "total_documents": collection.count(),
                "persist_directory": settings.CHROMA_DB_PATH
            }
        except Exception as e:
            logger.error(f"✗ Failed to get ChromaDB stats: {e}", exc_info=True)
            return {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "total_documents": 0,
                "persist_directory": settings.CHROMA_DB_PATH,
                "error": str(e)
            }