"""
API Routes for RAG Technique Comparison

Endpoints for retrieving and comparing RAG execution data
for dashboard visualization.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from db.models import RAGExecution

router = APIRouter()


def extract_top_scores(sources: Optional[list]) -> Optional[dict]:
    """
    Extract top 3 chunk scores from sources list.

    Supports multiple score key formats:
    - 'score': Used by baseline, graph, hyde, subquery
    - 'rerank_score': Used by reranking technique (preferred)
    - 'original_score': Fallback for reranking technique
    - 'original_scores': Used by fusion (list of scores from multiple queries)

    Args:
        sources: List of source dicts with score key

    Returns:
        Dict with top1, top2, top3 scores or None if no scores
    """
    if not sources or not isinstance(sources, list):
        return None

    # Extract all scores (check multiple possible keys)
    scores = []
    for source in sources:
        if isinstance(source, dict):
            # Priority: rerank_score > score > original_score > original_scores (max)
            if source.get('rerank_score') is not None:
                scores.append(float(source['rerank_score']))
            elif source.get('score') is not None:
                scores.append(float(source['score']))
            elif source.get('original_score') is not None:
                scores.append(float(source['original_score']))
            elif source.get('original_scores') is not None:
                # Fusion: original_scores é uma lista - pegar o máximo
                original_scores_list = source['original_scores']
                if isinstance(original_scores_list, list) and original_scores_list:
                    max_score = max(float(s) for s in original_scores_list)
                    scores.append(max_score)

    if not scores:
        return None

    # Sort descending and take top 3
    scores.sort(reverse=True)

    return {
        'top1': scores[0] if len(scores) > 0 else None,
        'top2': scores[1] if len(scores) > 1 else None,
        'top3': scores[2] if len(scores) > 2 else None,
        'avg': sum(scores[:3]) / min(len(scores), 3) if scores else None,
    }


@router.get("/comparison-data")
async def get_comparison_data(db: Session = Depends(get_db)) -> list[dict]:
    """
    Get all RAG execution data for technique comparison.

    Retrieves all executions from the database with their metrics,
    formatted for frontend dashboard consumption.

    Args:
        db: Database session (auto-injected)

    Returns:
        list[dict]: List of execution data with metrics

    Response Format:
        [
            {
                "technique": "baseline",
                "precision": 0.85,
                "recall": 0.82,
                "latency_ms": 245.3,
                "answer": "RAG is...",
                "query": "What is RAG?",
                "created_at": "2024-01-20T10:30:00",
                "faithfulness": 0.91,
                "answer_relevancy": 0.88
            },
            ...
        ]

    Notes:
        - Returns empty list if no executions found
        - Handles missing metrics gracefully (returns null/0.0)
        - Includes all RAGAS metrics for advanced analysis
    """
    # Query all executions with their metrics (eager loading)
    executions = db.query(RAGExecution).all()

    # Transform to response format
    comparison_data = []
    for exec in executions:
        # Build base data
        data = {
            "technique": exec.technique_name,
            "query": exec.query_text,
            "answer": exec.answer_text,
            "created_at": exec.created_at.isoformat() if exec.created_at else None,
        }

        # Add metrics if available
        if exec.metrics:
            data.update(
                {
                    "precision": exec.metrics.context_precision or 0.0,
                    "recall": exec.metrics.context_recall or 0.0,
                    "latency_ms": exec.metrics.latency_ms or 0.0,
                    "faithfulness": exec.metrics.faithfulness,
                    "answer_relevancy": exec.metrics.answer_relevancy,
                    "chunks_retrieved": exec.metrics.chunks_retrieved,
                }
            )
        else:
            # No metrics available - return default values
            data.update(
                {
                    "precision": 0.0,
                    "recall": 0.0,
                    "latency_ms": 0.0,
                    "faithfulness": None,
                    "answer_relevancy": None,
                    "chunks_retrieved": None,
                }
            )

        # Add top chunk scores from sources
        data["top_scores"] = extract_top_scores(exec.sources)

        comparison_data.append(data)

    return comparison_data
