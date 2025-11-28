"""
Helper functions for integrating database persistence with RAG techniques.

Provides decorator and utility functions to automatically persist
RAG execution results without modifying technique implementations.
"""

from functools import wraps
from typing import Callable, Dict, Any

from sqlalchemy.orm import Session

from .crud import create_execution


def persist_rag_execution(db: Session | None = None):
    """
    Decorator to automatically persist RAG execution results.

    Wraps RAG technique functions to save results to database after execution.
    Works with both sync and async functions.

    Args:
        db: Optional database session (if None, persistence is skipped)

    Returns:
        Decorator function

    Example:
        @persist_rag_execution(db=db)
        async def baseline_rag(query: str, **kwargs):
            # ... implementation ...
            return result

        # Or with manual session management:
        result = await baseline_rag("What is Python?")
        save_rag_result(db, result, technique="baseline")

    Note:
        Expected result format from RAG techniques:
        {
            "query": str,
            "answer": str,
            "sources": List[Dict],
            "metrics": Dict,
            "execution_details": Dict
        }
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Execute original function
            result = await func(*args, **kwargs)

            # Persist if database session provided
            if db is not None:
                _persist_result(db, result, func.__name__)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Execute original function
            result = func(*args, **kwargs)

            # Persist if database session provided
            if db is not None:
                _persist_result(db, result, func.__name__)

            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def save_rag_result(
    db: Session,
    result: Dict[str, Any],
    technique: str,
    namespace: str | None = None,
    top_k: int = 5,
) -> int:
    """
    Manually save a RAG execution result to database.

    Use this when you can't use the decorator or need more control
    over when results are persisted.

    Args:
        db: Database session
        result: RAG execution result dictionary
        technique: Technique name (baseline, hyde, reranking, etc)
        namespace: Optional Pinecone namespace
        top_k: Number of chunks retrieved

    Returns:
        Execution ID

    Example:
        >>> result = await baseline_rag("What is Python?")
        >>> execution_id = save_rag_result(
        ...     db,
        ...     result,
        ...     technique="baseline",
        ...     top_k=5
        ... )
        >>> print(f"Saved execution {execution_id}")

    Raises:
        ValueError: If result format is invalid
    """
    # Validate result format
    required_keys = {"query", "answer", "sources", "metrics", "execution_details"}
    if not all(key in result for key in required_keys):
        missing = required_keys - set(result.keys())
        raise ValueError(f"Invalid result format. Missing keys: {missing}")

    # Create execution record
    execution = create_execution(
        db,
        query=result["query"],
        answer=result["answer"],
        technique=technique,
        sources=result["sources"],
        metrics=result["metrics"],
        execution_details=result["execution_details"],
        top_k=top_k,
        namespace=namespace,
        metadata=result.get("metadata", {}),
        full_response=result,  # Save complete response object
    )

    return execution.id


def _persist_result(db: Session, result: Dict[str, Any], technique: str) -> None:
    """
    Internal helper to persist result.

    Args:
        db: Database session
        result: RAG execution result
        technique: Technique name
    """
    try:
        save_rag_result(db, result, technique)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to persist RAG result: {e}")


def get_or_create_session(db: Session | None = None) -> Session | None:
    """
    Get existing session or create a new one.

    Helper for managing database sessions in RAG techniques.

    Args:
        db: Optional existing session

    Returns:
        Database session or None

    Example:
        db_session = get_or_create_session(db)
        if db_session:
            save_rag_result(db_session, result, "baseline")
    """
    if db is not None:
        return db

    # Optionally create a new session (not recommended in production)
    # from .database import SessionLocal
    # return SessionLocal()

    return None
