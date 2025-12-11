"""
Simple RAG system for querying company information.
"""

from typing import List, Dict, Tuple
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from src.vectorstore.chroma_store import ChromaStore
from src.config import settings

logger = logging.getLogger(__name__)


class CompanyRAG:
    """Simple RAG system for company intelligence queries."""

    def __init__(self):
        self.vector_store = ChromaStore()

        self.llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS
        )

        # System prompt
        self.system_prompt = """You are a knowledgeable assistant helping users learn about companies.

Your role:
- Answer questions accurately using the provided company information
- Cite sources by mentioning the company name
- If the answer isn't in the provided context, say so honestly
- Be concise but informative

When answering, focus on being helpful and accurate."""
        
        logger.info("CompanyRAG initialized")
    
    def query(
        self,
        question: str,
        company_name: str = None,
        k: int = 5
    ) -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            company_name: Optional company to filter by
            k: Number of chunks to retrieve
            
        Returns:
            (answer, sources) tuple
        """
        logger.info(f"Processing query: '{question}'")

        # 1. Retrieve relevant chunks
        chunks = self.vector_store.search_companies(
            query=question,
            company_name=company_name,
            k=k
        )

        if not chunks:
            return "I don't have information about that. Try asking about a company that's been scraped.", []
    
        # 2. Build context from chunks
        context = self.build_context(chunks)

            # 3. Generate answer with LLM
        messages = [
        SystemMessage(content=self.system_prompt),
        HumanMessage(content=f"""Context from company information:
{context}

User question: {question}

Please provide a detailed answer based on the context above.""")
        ]

        try:
            response = self.llm.invoke(messages)
            answer = response.content
            
            logger.info("Generated answer successfully")
            return answer, chunks
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            return error_msg, chunks




    def build_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            company = chunk['company_name']
            source_info = f"[Source {i}: {company}]"
            context_parts.append(f"{source_info}\n{chunk['content']}\n")
        
        return "\n".join(context_parts)