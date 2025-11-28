"""
Database persistence routes for RAG Lab.

Endpoints for querying execution history, statistics, and analytics.
Separate from main routes for better organization.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db import (
    get_db,
    get_execution,
    get_executions,
    get_executions_by_technique,
    get_recent_executions,
    get_technique_statistics,
    check_database_health,
)
from models.schemas import RAGTechnique

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/health")
async def database_health():
    """
    Check database health and connectivity.

    Returns:
        dict: Database health status

    Example:
        GET /api/db/health
        {
            "status": "healthy",
            "database": "/path/to/rag_lab.db",
            "tables": 2,
            "table_names": ["rag_executions", "rag_metrics"]
        }
    """
    return check_database_health()


@router.get("/executions/{execution_id}")
async def get_execution_by_id(
    execution_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single execution by ID.

    Args:
        execution_id: Execution ID

    Returns:
        Execution details with metrics

    Raises:
        HTTPException: If execution not found

    Example:
        GET /api/db/executions/1
        {
            "id": 1,
            "query": "What is Python?",
            "answer": "Python is a high-level...",
            "technique": "baseline",
            "metrics": {...},
            ...
        }
    """
    execution = get_execution(db, execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    return execution.to_dict()


@router.get("/executions")
async def list_executions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    technique: Optional[str] = Query(None, description="Filter by technique name"),
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    hours: Optional[int] = Query(None, ge=1, description="Filter by last N hours"),
    db: Session = Depends(get_db),
):
    """
    List executions with filtering and pagination.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        technique: Filter by technique name (baseline, hyde, etc)
        namespace: Filter by Pinecone namespace
        hours: Filter by last N hours

    Returns:
        List of execution records

    Examples:
        GET /api/db/executions?limit=10
        GET /api/db/executions?technique=baseline&limit=20
        GET /api/db/executions?hours=24
    """
    # If hours filter specified, use time-based query
    if hours is not None:
        executions = get_recent_executions(db, hours=hours, limit=limit)
    else:
        # Calculate date filters if needed
        start_date = None
        end_date = None

        executions = get_executions(
            db,
            skip=skip,
            limit=limit,
            technique=technique,
            namespace=namespace,
            start_date=start_date,
            end_date=end_date,
        )

    return {
        "executions": [exec.to_dict() for exec in executions],
        "count": len(executions),
        "skip": skip,
        "limit": limit,
        "filters": {
            "technique": technique,
            "namespace": namespace,
            "hours": hours,
        },
    }


@router.get("/executions/technique/{technique}")
async def get_technique_executions(
    technique: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get all executions for a specific technique.

    Args:
        technique: Technique name (baseline, hyde, reranking, agentic)
        limit: Maximum number of records

    Returns:
        List of executions for the technique

    Example:
        GET /api/db/executions/technique/baseline?limit=50
    """
    executions = get_executions_by_technique(db, technique, limit=limit)

    return {
        "technique": technique,
        "executions": [exec.to_dict() for exec in executions],
        "count": len(executions),
    }


@router.get("/executions/recent")
async def list_recent_executions(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get recent executions from last N hours.

    Args:
        hours: Number of hours to look back (default: 24, max: 168/7 days)
        limit: Maximum number of records

    Returns:
        List of recent executions

    Example:
        GET /api/db/executions/recent?hours=1
        GET /api/db/executions/recent?hours=24&limit=50
    """
    executions = get_recent_executions(db, hours=hours, limit=limit)

    return {
        "executions": [exec.to_dict() for exec in executions],
        "count": len(executions),
        "hours": hours,
        "limit": limit,
    }


@router.get("/statistics")
async def get_all_statistics(
    days: int = Query(30, ge=1, le=365, description="Days to include in statistics"),
    db: Session = Depends(get_db),
):
    """
    Get aggregated statistics for all techniques.

    Provides comprehensive performance metrics:
    - Total executions per technique
    - Average/min/max latency
    - Average/total cost
    - Average/total tokens
    - Quality metrics (if available)

    Args:
        days: Number of days to include (default: 30, max: 365)

    Returns:
        Statistics aggregated by technique

    Example:
        GET /api/db/statistics?days=7
        {
            "techniques": {
                "baseline": {
                    "total_executions": 100,
                    "latency": {"avg_ms": 850, "min_ms": 600, "max_ms": 1200},
                    "cost": {"avg_usd": 0.002, "total_usd": 0.20},
                    ...
                },
                "hyde": {...}
            },
            "period_days": 7,
            "total_techniques": 2
        }
    """
    stats = get_technique_statistics(db, technique=None, days=days)
    return stats


@router.get("/statistics/technique/{technique}")
async def get_technique_stats(
    technique: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Get statistics for a specific technique.

    Args:
        technique: Technique name (baseline, hyde, reranking, agentic)
        days: Number of days to include in statistics

    Returns:
        Statistics for the technique

    Example:
        GET /api/db/statistics/technique/baseline?days=7
        {
            "technique": "baseline",
            "total_executions": 50,
            "latency": {"avg_ms": 850, "min_ms": 600, "max_ms": 1200},
            "cost": {"avg_usd": 0.002, "total_usd": 0.10},
            "tokens": {"avg": 1200, "total": 60000},
            "quality": {
                "context_precision": 0.85,
                "context_recall": 0.78,
                ...
            },
            "period_days": 7
        }
    """
    stats = get_technique_statistics(db, technique=technique, days=days)
    return stats


@router.get("/statistics/comparison")
async def compare_techniques(
    techniques: list[str] = Query(..., description="Techniques to compare"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Compare statistics across multiple techniques.

    Args:
        techniques: List of technique names to compare
        days: Number of days to include

    Returns:
        Comparative statistics

    Example:
        GET /api/db/statistics/comparison?techniques=baseline&techniques=hyde&days=7
        {
            "comparison": {
                "baseline": {...},
                "hyde": {...}
            },
            "period_days": 7
        }
    """
    comparison = {}

    for technique in techniques:
        stats = get_technique_statistics(db, technique=technique, days=days)
        comparison[technique] = stats

    return {
        "comparison": comparison,
        "period_days": days,
        "techniques_compared": len(techniques),
    }


@router.get("/analytics/timeline")
async def execution_timeline(
    technique: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Get execution timeline data for visualization.

    Args:
        technique: Optional technique filter
        hours: Hours to look back

    Returns:
        Timeline data with execution counts and metrics

    Example:
        GET /api/db/analytics/timeline?technique=baseline&hours=24
    """
    executions = get_recent_executions(db, hours=hours, limit=1000)

    # Filter by technique if specified
    if technique:
        executions = [e for e in executions if e.technique_name == technique]

    # Group by hour
    timeline = {}
    for execution in executions:
        hour_key = execution.created_at.strftime("%Y-%m-%d %H:00")
        if hour_key not in timeline:
            timeline[hour_key] = {
                "timestamp": hour_key,
                "count": 0,
                "avg_latency_ms": 0,
                "total_cost_usd": 0,
            }

        timeline[hour_key]["count"] += 1
        if execution.metrics:
            timeline[hour_key]["avg_latency_ms"] += execution.metrics.latency_ms
            timeline[hour_key]["total_cost_usd"] += execution.metrics.cost_total_usd or 0

    # Calculate averages
    for data in timeline.values():
        if data["count"] > 0:
            data["avg_latency_ms"] = round(data["avg_latency_ms"] / data["count"], 2)
            data["total_cost_usd"] = round(data["total_cost_usd"], 6)

    return {
        "timeline": sorted(timeline.values(), key=lambda x: x["timestamp"]),
        "total_executions": len(executions),
        "technique": technique,
        "hours": hours,
    }
