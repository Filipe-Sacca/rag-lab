"""
Google Text Embedding Configuration

Handles initialization and configuration of Google's text-embedding-004 model.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings


def get_embedding_model(
    model_name: str | None = None,
    task_type: str = "retrieval_document",
) -> GoogleGenerativeAIEmbeddings:
    """
    Get configured Google embedding model instance.

    Args:
        model_name: Embedding model name (defaults to settings.EMBEDDING_MODEL)
        task_type: Task type for embeddings:
            - "retrieval_document": For indexing documents
            - "retrieval_query": For query embeddings
            - "semantic_similarity": For similarity tasks
            - "classification": For classification tasks

    Returns:
        GoogleGenerativeAIEmbeddings: Configured embedding model

    Example:
        >>> embeddings = get_embedding_model()
        >>> vector = embeddings.embed_query("What is RAG?")
        >>> doc_vectors = embeddings.embed_documents(["doc1", "doc2"])
    """
    return GoogleGenerativeAIEmbeddings(
        model=model_name or settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        task_type=task_type,
    )


def get_query_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Get embedding model configured for query embeddings.

    Returns:
        GoogleGenerativeAIEmbeddings: Query-optimized embedding model
    """
    return get_embedding_model(task_type="retrieval_query")


def get_document_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Get embedding model configured for document embeddings.

    Returns:
        GoogleGenerativeAIEmbeddings: Document-optimized embedding model
    """
    return get_embedding_model(task_type="retrieval_document")
