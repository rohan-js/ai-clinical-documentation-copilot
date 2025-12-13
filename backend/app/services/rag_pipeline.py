"""
RAG (Retrieval Augmented Generation) pipeline.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import logging
from typing import List, Optional, Dict, Any

from app.config import settings
from app.data.clinical_guidelines import (
    get_guideline_texts,
    get_guideline_ids,
    get_guideline_metadata,
    CLINICAL_GUIDELINES
)

logger = logging.getLogger(__name__)

# Global instances (lazy loaded)
_embedding_model = None
_chroma_client = None
_collection = None

COLLECTION_NAME = "clinical_guidelines"


def get_embedding_model():
    """Get or initialize the sentence-transformers embedding model."""
    global _embedding_model
    
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            _embedding_model = SentenceTransformer(settings.embedding_model)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    return _embedding_model


def get_chroma_collection():
    """Get or initialize the ChromaDB collection."""
    global _chroma_client, _collection
    
    if _collection is None:
        try:
            import chromadb
            
            logger.info("Initializing ChromaDB")
            
            # Create persistent client
            _chroma_client = chromadb.PersistentClient(path=str(settings.chroma_dir))
            
            # Get or create collection
            _collection = _chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Clinical guidelines for audiology"}
            )
            
            # Check if we need to populate the collection
            if _collection.count() == 0:
                populate_guidelines()
            
            logger.info(f"ChromaDB collection ready with {_collection.count()} documents")
            
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            # Fallback to in-memory mode
            try:
                import chromadb
                _chroma_client = chromadb.Client()
                _collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)
                
                if _collection.count() == 0:
                    populate_guidelines()
                    
                logger.info(f"Using in-memory ChromaDB with {_collection.count()} documents")
            except Exception as e2:
                logger.error(f"In-memory ChromaDB also failed: {e2}")
                raise RuntimeError(f"Failed to initialize ChromaDB: {e2}")
    
    return _collection


def populate_guidelines():
    """Populate the ChromaDB collection with clinical guidelines."""
    try:
        collection = _collection
        model = get_embedding_model()
        
        texts = get_guideline_texts()
        ids = get_guideline_ids()
        metadatas = get_guideline_metadata()
        
        logger.info(f"Embedding {len(texts)} clinical guidelines")
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        
        # Add to collection
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info("Clinical guidelines populated successfully")
        
    except Exception as e:
        logger.error(f"Failed to populate guidelines: {e}")
        raise


def embed_text(text: str) -> List[float]:
    """
    Generate embeddings for a text.
    
    Args:
        text: Text to embed
        
    Returns:
        List of embedding floats
    """
    model = get_embedding_model()
    embedding = model.encode(text, show_progress_bar=False)
    return embedding.tolist()


def retrieve_relevant_guidelines(
    query: str,
    top_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant clinical guidelines based on query.
    
    Args:
        query: Search query (extracted entities or clinical text)
        top_k: Number of results to return
        
    Returns:
        List of relevant guideline documents with metadata
    """
    try:
        collection = get_chroma_collection()
        k = top_k or settings.rag_top_k
        
        # Generate query embedding
        query_embedding = embed_text(query)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        guidelines = []
        
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                guidelines.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        
        logger.info(f"Retrieved {len(guidelines)} relevant guidelines")
        return guidelines
        
    except Exception as e:
        logger.error(f"Guideline retrieval failed: {e}")
        return []


def retrieve_guidelines_for_entities(entities_dict: Dict[str, Any]) -> List[str]:
    """
    Retrieve relevant guidelines based on extracted clinical entities.
    
    Args:
        entities_dict: Dictionary of extracted entities
        
    Returns:
        List of relevant guideline texts
    """
    # Create a combined query from entities
    query_parts = []
    
    # Add symptoms
    if entities_dict.get("symptoms"):
        query_parts.extend(entities_dict["symptoms"])
    
    # Add assessments
    if entities_dict.get("assessments"):
        query_parts.extend(entities_dict["assessments"])
    
    # Add audiological findings
    if entities_dict.get("audiological_findings"):
        query_parts.extend(entities_dict["audiological_findings"])
    
    # Add recommendations
    if entities_dict.get("recommendations"):
        query_parts.extend(entities_dict["recommendations"])
    
    if not query_parts:
        # Fallback: use all entity values
        for key, value in entities_dict.items():
            if isinstance(value, list):
                query_parts.extend(value)
            elif isinstance(value, dict):
                query_parts.extend(value.values())
    
    # Combine into query
    query = " ".join(str(p) for p in query_parts[:20])  # Limit to prevent too long query
    
    if not query.strip():
        return []
    
    # Retrieve guidelines
    results = retrieve_relevant_guidelines(query, top_k=5)
    
    return [r["content"] for r in results]


def enhance_with_rag(
    extracted_entities: Dict[str, Any],
    clinical_text: str
) -> List[str]:
    """
    Enhance processing with RAG - retrieve relevant guidelines.
    
    Args:
        extracted_entities: Dictionary of extracted clinical entities
        clinical_text: Original clinical text
        
    Returns:
        List of relevant guideline texts to use as context
    """
    try:
        # First, try entity-based retrieval
        entity_guidelines = retrieve_guidelines_for_entities(extracted_entities)
        
        # If we got fewer results, supplement with text-based retrieval
        if len(entity_guidelines) < 3:
            # Use first 1000 chars of clinical text as query
            text_query = clinical_text[:1000] if clinical_text else ""
            if text_query:
                text_guidelines = retrieve_relevant_guidelines(text_query, top_k=3)
                entity_guidelines.extend([g["content"] for g in text_guidelines])
        
        # Deduplicate while preserving order
        seen = set()
        unique_guidelines = []
        for g in entity_guidelines:
            if g not in seen:
                seen.add(g)
                unique_guidelines.append(g)
        
        return unique_guidelines[:5]  # Return top 5
        
    except Exception as e:
        logger.error(f"RAG enhancement failed: {e}")
        return []


def get_collection_stats() -> Dict[str, Any]:
    """Get statistics about the ChromaDB collection."""
    try:
        collection = get_chroma_collection()
        return {
            "collection_name": COLLECTION_NAME,
            "document_count": collection.count(),
            "embedding_model": settings.embedding_model
        }
    except Exception as e:
        return {
            "error": str(e)
        }
