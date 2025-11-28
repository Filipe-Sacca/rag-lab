"""
Pinecone Vector Store Configuration

Handles initialization and connection to Pinecone vector database.
"""

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from config import settings
from core.embeddings import get_document_embedding_model


def get_pinecone_client() -> Pinecone:
    """
    Get configured Pinecone client.

    Returns:
        Pinecone: Configured Pinecone client instance

    Example:
        >>> pc = get_pinecone_client()
        >>> indexes = pc.list_indexes()
    """
    return Pinecone(api_key=settings.PINECONE_API_KEY)


def create_index_if_not_exists(
    index_name: str | None = None,
    dimension: int = 768,
    metric: str = "cosine",
) -> None:
    """
    Create Pinecone index if it doesn't exist.

    Args:
        index_name: Index name (defaults to settings.PINECONE_INDEX_NAME)
        dimension: Vector dimension (768 for text-embedding-004)
        metric: Distance metric ("cosine", "euclidean", "dotproduct")

    Note:
        text-embedding-004 produces 768-dimensional embeddings
    """
    pc = get_pinecone_client()
    index_name = index_name or settings.PINECONE_INDEX_NAME

    existing_indexes = [index.name for index in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.PINECONE_ENVIRONMENT,
            ),
        )
        print(f"Created Pinecone index: {index_name}")
    else:
        print(f"Pinecone index already exists: {index_name}")


def get_vector_store(
    index_name: str | None = None,
    namespace: str | None = None,
) -> PineconeVectorStore:
    """
    Get Pinecone vector store instance.

    Args:
        index_name: Index name (defaults to settings.PINECONE_INDEX_NAME)
        namespace: Namespace for organizing vectors (optional)

    Returns:
        PineconeVectorStore: Configured vector store

    Example:
        >>> vector_store = get_vector_store()
        >>> results = vector_store.similarity_search("query", k=5)
    """
    index_name = index_name or settings.PINECONE_INDEX_NAME
    namespace = namespace or settings.PINECONE_NAMESPACE
    embeddings = get_document_embedding_model()

    return PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
        pinecone_api_key=settings.PINECONE_API_KEY,
    )


def delete_index(index_name: str | None = None) -> None:
    """
    Delete Pinecone index.

    Args:
        index_name: Index name (defaults to settings.PINECONE_INDEX_NAME)

    Warning:
        This permanently deletes the index and all its data.
    """
    pc = get_pinecone_client()
    index_name = index_name or settings.PINECONE_INDEX_NAME

    pc.delete_index(index_name)
    print(f"Deleted Pinecone index: {index_name}")
