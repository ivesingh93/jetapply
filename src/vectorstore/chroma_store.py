import logging

from src.models import JobMetadata, JobPosting
from src.config import settings
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import Optional

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