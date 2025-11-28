"""
Analysis Service for RAG Lab

Handles persistence and retrieval of RAG Analyst agent analyses.
Provides filtering by timestamp for historical analysis lookup.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.models import RAGAnalysis


def save_analysis(
    db: Session,
    question: str,
    response: str,
    tool_calls: List[Dict],
    iterations: int,
    duration_ms: Optional[float] = None,
    analysis_data: Optional[Dict[str, Any]] = None,
) -> RAGAnalysis:
    """
    Save a new analysis to the database.

    Args:
        db: Database session
        question: User's question
        response: Agent's response
        tool_calls: List of tools used
        iterations: Number of tool call iterations
        duration_ms: Execution time in milliseconds
        analysis_data: Full structured analysis data (aggregated_data, rankings, etc.)

    Returns:
        Created RAGAnalysis instance
    """
    analysis = RAGAnalysis(
        question=question,
        response=response,
        tool_calls=tool_calls,
        iterations=iterations,
        duration_ms=duration_ms,
        analysis_data=analysis_data,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_by_id(db: Session, analysis_id: int) -> Optional[RAGAnalysis]:
    """
    Get a specific analysis by ID.

    Args:
        db: Database session
        analysis_id: Analysis ID

    Returns:
        RAGAnalysis instance or None
    """
    return db.query(RAGAnalysis).filter(RAGAnalysis.id == analysis_id).first()


def list_analyses(
    db: Session,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    List analyses with optional timestamp filtering.

    Args:
        db: Database session
        date_from: Filter analyses from this date (inclusive)
        date_to: Filter analyses until this date (inclusive)
        limit: Maximum number of results (default 50, max 100)
        offset: Number of results to skip

    Returns:
        Dict with total count and list of analyses
    """
    # Cap limit at 100
    limit = min(limit, 100)

    # Build query
    query = db.query(RAGAnalysis)

    # Apply date filters
    if date_from:
        query = query.filter(RAGAnalysis.created_at >= date_from)
    if date_to:
        query = query.filter(RAGAnalysis.created_at <= date_to)

    # Get total count before pagination
    total = query.count()

    # Apply ordering and pagination
    analyses = (
        query
        .order_by(desc(RAGAnalysis.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "analyses": [a.to_dict() for a in analyses],
    }


def delete_analysis(db: Session, analysis_id: int) -> bool:
    """
    Delete an analysis by ID.

    Args:
        db: Database session
        analysis_id: Analysis ID

    Returns:
        True if deleted, False if not found
    """
    analysis = db.query(RAGAnalysis).filter(RAGAnalysis.id == analysis_id).first()
    if not analysis:
        return False

    db.delete(analysis)
    db.commit()
    return True


def get_analyses_summary(db: Session) -> Dict[str, Any]:
    """
    Get summary statistics of all analyses.

    Args:
        db: Database session

    Returns:
        Dict with summary statistics
    """
    from sqlalchemy import func

    total = db.query(func.count(RAGAnalysis.id)).scalar() or 0
    avg_iterations = db.query(func.avg(RAGAnalysis.iterations)).scalar() or 0
    avg_duration = db.query(func.avg(RAGAnalysis.duration_ms)).scalar() or 0

    # Get date range
    oldest = db.query(func.min(RAGAnalysis.created_at)).scalar()
    newest = db.query(func.max(RAGAnalysis.created_at)).scalar()

    return {
        "total_analyses": total,
        "avg_iterations": round(avg_iterations, 2),
        "avg_duration_ms": round(avg_duration, 2) if avg_duration else None,
        "date_range": {
            "oldest": oldest.isoformat() if oldest else None,
            "newest": newest.isoformat() if newest else None,
        },
    }
