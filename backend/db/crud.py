"""
CRUD operations for RAG Lab database.

Provides create, read, update, delete operations for RAG executions
and metrics, with support for filtering, aggregation, and statistics.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from .models import RAGExecution, RAGMetric


def create_execution(
    db: Session,
    query: str,
    answer: str,
    technique: str,
    sources: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    execution_details: Dict[str, Any],
    top_k: int = 5,
    namespace: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    full_response: Optional[Dict[str, Any]] = None,
) -> RAGExecution:
    """
    Create a new RAG execution record with metrics.

    Automatically creates both RAGExecution and RAGMetric records
    in a single transaction.

    Args:
        db: Database session
        query: User query text
        answer: Generated answer
        technique: RAG technique name (baseline, hyde, reranking, etc)
        sources: List of retrieved chunks with scores and metadata
        metrics: Performance metrics dict (latency, tokens, cost)
        execution_details: Execution details dict (steps, timings)
        top_k: Number of chunks retrieved
        namespace: Optional Pinecone namespace
        metadata: Additional metadata

    Returns:
        RAGExecution: Created execution record with metrics

    Example:
        >>> result = await baseline_rag("What is Python?")
        >>> execution = create_execution(
        ...     db,
        ...     query=result["query"],
        ...     answer=result["answer"],
        ...     technique="baseline",
        ...     sources=result["sources"],
        ...     metrics=result["metrics"],
        ...     execution_details=result["execution_details"]
        ... )
        >>> print(execution.id, execution.metrics.latency_ms)
        1 842.5
    """
    # Create execution record
    execution = RAGExecution(
        query_text=query,
        answer_text=answer,
        technique_name=technique,
        top_k=top_k,
        namespace=namespace,
        sources=sources,
        execution_details=execution_details,
        extra_metadata=metadata or {},
        full_response=full_response,
    )

    # Create metrics record
    metric = RAGMetric(
        execution=execution,
        latency_ms=metrics.get("latency_ms", 0.0),
        latency_seconds=metrics.get("latency_seconds", 0.0),
        tokens_input=metrics.get("tokens", {}).get("input"),
        tokens_output=metrics.get("tokens", {}).get("output"),
        tokens_total=metrics.get("tokens", {}).get("total"),
        cost_input_usd=metrics.get("cost", {}).get("input_usd"),
        cost_output_usd=metrics.get("cost", {}).get("output_usd"),
        cost_total_usd=metrics.get("cost", {}).get("total_usd"),
        context_precision=metrics.get("context_precision"),
        context_recall=metrics.get("context_recall"),
        faithfulness=metrics.get("faithfulness"),
        answer_relevancy=metrics.get("answer_relevancy"),
        chunks_retrieved=metrics.get("chunks_retrieved"),
    )

    # Add to session and commit
    db.add(execution)
    db.add(metric)
    db.commit()
    db.refresh(execution)

    return execution


def get_execution(db: Session, execution_id: int) -> Optional[RAGExecution]:
    """
    Get a single execution by ID.

    Args:
        db: Database session
        execution_id: Execution ID

    Returns:
        RAGExecution or None if not found

    Example:
        >>> execution = get_execution(db, 1)
        >>> print(execution.query_text)
        What is Python?
    """
    return db.query(RAGExecution).filter(RAGExecution.id == execution_id).first()


def get_executions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    technique: Optional[str] = None,
    namespace: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[RAGExecution]:
    """
    Get executions with optional filtering and pagination.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        technique: Filter by technique name
        namespace: Filter by namespace
        start_date: Filter by minimum creation date
        end_date: Filter by maximum creation date

    Returns:
        List of RAGExecution records

    Example:
        >>> # Get last 10 baseline executions
        >>> executions = get_executions(
        ...     db,
        ...     technique="baseline",
        ...     limit=10
        ... )

        >>> # Get executions from last 7 days
        >>> from datetime import datetime, timedelta
        >>> start = datetime.utcnow() - timedelta(days=7)
        >>> recent = get_executions(db, start_date=start)
    """
    query = db.query(RAGExecution)

    # Apply filters
    if technique:
        query = query.filter(RAGExecution.technique_name == technique)
    if namespace:
        query = query.filter(RAGExecution.namespace == namespace)
    if start_date:
        query = query.filter(RAGExecution.created_at >= start_date)
    if end_date:
        query = query.filter(RAGExecution.created_at <= end_date)

    # Order by most recent first
    query = query.order_by(desc(RAGExecution.created_at))

    # Pagination
    return query.offset(skip).limit(limit).all()


def get_executions_by_technique(
    db: Session,
    technique: str,
    limit: int = 100,
) -> List[RAGExecution]:
    """
    Get all executions for a specific technique.

    Args:
        db: Database session
        technique: Technique name (baseline, hyde, reranking, etc)
        limit: Maximum number of records

    Returns:
        List of RAGExecution records

    Example:
        >>> hyde_executions = get_executions_by_technique(db, "hyde")
        >>> print(f"Found {len(hyde_executions)} HyDE executions")
    """
    return get_executions(db, technique=technique, limit=limit)


def get_recent_executions(
    db: Session,
    hours: int = 24,
    limit: int = 100,
) -> List[RAGExecution]:
    """
    Get recent executions from the last N hours.

    Args:
        db: Database session
        hours: Number of hours to look back
        limit: Maximum number of records

    Returns:
        List of RAGExecution records

    Example:
        >>> # Get all executions from last 24 hours
        >>> recent = get_recent_executions(db, hours=24)

        >>> # Get last hour's executions
        >>> last_hour = get_recent_executions(db, hours=1)
    """
    start_date = datetime.utcnow() - timedelta(hours=hours)
    return get_executions(db, start_date=start_date, limit=limit)


def get_technique_statistics(
    db: Session,
    technique: Optional[str] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get aggregated statistics for a technique or all techniques.

    Calculates:
    - Total executions
    - Average latency
    - Average cost
    - Average tokens
    - Average quality metrics (if available)

    Args:
        db: Database session
        technique: Optional technique name (None for all techniques)
        days: Number of days to include in statistics

    Returns:
        Dict with aggregated statistics

    Example:
        >>> # Statistics for all techniques
        >>> stats = get_technique_statistics(db)
        >>> print(stats["baseline"]["avg_latency_ms"])
        850.5

        >>> # Statistics for specific technique
        >>> hyde_stats = get_technique_statistics(db, technique="hyde")
        >>> print(hyde_stats["avg_cost_usd"])
        0.004
    """
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)

    # Base query
    query = (
        db.query(
            RAGExecution.technique_name,
            func.count(RAGExecution.id).label("total_executions"),
            func.avg(RAGMetric.latency_ms).label("avg_latency_ms"),
            func.min(RAGMetric.latency_ms).label("min_latency_ms"),
            func.max(RAGMetric.latency_ms).label("max_latency_ms"),
            func.avg(RAGMetric.cost_total_usd).label("avg_cost_usd"),
            func.sum(RAGMetric.cost_total_usd).label("total_cost_usd"),
            func.avg(RAGMetric.tokens_total).label("avg_tokens"),
            func.sum(RAGMetric.tokens_total).label("total_tokens"),
            func.avg(RAGMetric.context_precision).label("avg_context_precision"),
            func.avg(RAGMetric.context_recall).label("avg_context_recall"),
            func.avg(RAGMetric.faithfulness).label("avg_faithfulness"),
            func.avg(RAGMetric.answer_relevancy).label("avg_answer_relevancy"),
        )
        .join(RAGMetric, RAGExecution.id == RAGMetric.execution_id)
        .filter(RAGExecution.created_at >= start_date)
    )

    # Filter by technique if specified
    if technique:
        query = query.filter(RAGExecution.technique_name == technique)

    # Group by technique
    query = query.group_by(RAGExecution.technique_name)

    # Execute query
    results = query.all()

    # Format results
    if technique:
        # Single technique stats
        if not results:
            return {
                "technique": technique,
                "total_executions": 0,
                "message": f"No executions found for technique '{technique}' in the last {days} days",
            }

        row = results[0]
        return {
            "technique": row.technique_name,
            "total_executions": row.total_executions,
            "latency": {
                "avg_ms": round(row.avg_latency_ms, 2) if row.avg_latency_ms else None,
                "min_ms": round(row.min_latency_ms, 2) if row.min_latency_ms else None,
                "max_ms": round(row.max_latency_ms, 2) if row.max_latency_ms else None,
            },
            "cost": {
                "avg_usd": round(row.avg_cost_usd, 6) if row.avg_cost_usd else None,
                "total_usd": round(row.total_cost_usd, 6) if row.total_cost_usd else None,
            },
            "tokens": {
                "avg": int(row.avg_tokens) if row.avg_tokens else None,
                "total": int(row.total_tokens) if row.total_tokens else None,
            },
            "quality": {
                "context_precision": round(row.avg_context_precision, 3) if row.avg_context_precision else None,
                "context_recall": round(row.avg_context_recall, 3) if row.avg_context_recall else None,
                "faithfulness": round(row.avg_faithfulness, 3) if row.avg_faithfulness else None,
                "answer_relevancy": round(row.avg_answer_relevancy, 3) if row.avg_answer_relevancy else None,
            },
            "period_days": days,
        }
    else:
        # All techniques stats
        stats_by_technique = {}
        for row in results:
            stats_by_technique[row.technique_name] = {
                "total_executions": row.total_executions,
                "latency": {
                    "avg_ms": round(row.avg_latency_ms, 2) if row.avg_latency_ms else None,
                    "min_ms": round(row.min_latency_ms, 2) if row.min_latency_ms else None,
                    "max_ms": round(row.max_latency_ms, 2) if row.max_latency_ms else None,
                },
                "cost": {
                    "avg_usd": round(row.avg_cost_usd, 6) if row.avg_cost_usd else None,
                    "total_usd": round(row.total_cost_usd, 6) if row.total_cost_usd else None,
                },
                "tokens": {
                    "avg": int(row.avg_tokens) if row.avg_tokens else None,
                    "total": int(row.total_tokens) if row.total_tokens else None,
                },
                "quality": {
                    "context_precision": round(row.avg_context_precision, 3) if row.avg_context_precision else None,
                    "context_recall": round(row.avg_context_recall, 3) if row.avg_context_recall else None,
                    "faithfulness": round(row.avg_faithfulness, 3) if row.avg_faithfulness else None,
                    "answer_relevancy": round(row.avg_answer_relevancy, 3) if row.avg_answer_relevancy else None,
                },
            }

        return {
            "techniques": stats_by_technique,
            "period_days": days,
            "total_techniques": len(stats_by_technique),
        }


def delete_old_executions(
    db: Session,
    days: int = 90,
) -> int:
    """
    Delete executions older than specified days.

    Useful for database maintenance and cleanup.
    Metrics are automatically deleted via cascade.

    Args:
        db: Database session
        days: Delete executions older than this many days

    Returns:
        Number of deleted executions

    Example:
        >>> # Delete executions older than 90 days
        >>> deleted = delete_old_executions(db, days=90)
        >>> print(f"Deleted {deleted} old executions")
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    deleted = (
        db.query(RAGExecution)
        .filter(RAGExecution.created_at < cutoff_date)
        .delete()
    )
    db.commit()
    return deleted
