"""
RAG Analyst - Tools Module

Database query tools for the RAG Analyst agent.
Each tool provides specific data access for analysis.

Tools Available:
1. list_available_techniques - List all techniques with execution counts
2. get_technique_stats - Detailed stats for one technique
3. compare_techniques - Head-to-head comparison of two techniques
4. get_best_technique - Find best technique for a metric
5. get_execution_details - Recent executions with queries/answers
6. get_anomalies - Detect performance anomalies
"""

import json
from typing import List

from langchain_core.tools import tool
from sqlalchemy import func, desc

from db.database import get_db
from db.models import RAGExecution, RAGMetric


# ============================================
# Tool: List Available Techniques
# ============================================
@tool
def list_available_techniques() -> str:
    """
    List all available RAG techniques in the database with execution counts.

    Returns:
        JSON with list of techniques and their execution counts.
    """
    db = next(get_db())
    try:
        results = db.query(
            RAGExecution.technique_name,
            func.count(RAGExecution.id).label('count'),
            func.max(RAGExecution.created_at).label('last_execution'),
        ).group_by(RAGExecution.technique_name).all()

        techniques = []
        for r in results:
            techniques.append({
                "name": r.technique_name,
                "executions": r.count,
                "last_execution": r.last_execution.isoformat() if r.last_execution else None,
            })

        return json.dumps({
            "total_techniques": len(techniques),
            "techniques": sorted(techniques, key=lambda x: x["executions"], reverse=True)
        }, indent=2)
    finally:
        db.close()


# ============================================
# Tool: Get Technique Stats
# ============================================
@tool
def get_technique_stats(technique_name: str) -> str:
    """
    Get detailed statistics for a specific RAG technique.

    Args:
        technique_name: Name of the technique (e.g., 'baseline', 'reranking', 'hyde')

    Returns:
        JSON string with aggregated statistics including latency, quality metrics, and execution count.
    """
    db = next(get_db())
    try:
        result = db.query(
            func.count(RAGExecution.id).label('total_executions'),
            func.avg(RAGMetric.latency_ms).label('avg_latency_ms'),
            func.min(RAGMetric.latency_ms).label('min_latency_ms'),
            func.max(RAGMetric.latency_ms).label('max_latency_ms'),
            func.avg(RAGMetric.faithfulness).label('avg_faithfulness'),
            func.avg(RAGMetric.answer_relevancy).label('avg_answer_relevancy'),
            func.avg(RAGMetric.context_precision).label('avg_context_precision'),
            func.avg(RAGMetric.context_recall).label('avg_context_recall'),
            func.avg(RAGMetric.chunks_retrieved).label('avg_chunks'),
        ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id
        ).filter(RAGExecution.technique_name == technique_name
        ).first()

        if not result or result.total_executions == 0:
            return json.dumps({"error": f"No data found for technique '{technique_name}'"})

        return json.dumps({
            "technique": technique_name,
            "total_executions": result.total_executions,
            "latency": {
                "avg_ms": round(result.avg_latency_ms or 0, 2),
                "min_ms": round(result.min_latency_ms or 0, 2),
                "max_ms": round(result.max_latency_ms or 0, 2),
            },
            "quality": {
                "faithfulness": round((result.avg_faithfulness or 0) * 100, 1),
                "answer_relevancy": round((result.avg_answer_relevancy or 0) * 100, 1),
                "context_precision": round((result.avg_context_precision or 0) * 100, 1),
                "context_recall": round((result.avg_context_recall or 0) * 100, 1),
            },
            "avg_chunks_retrieved": round(result.avg_chunks or 0, 1),
        }, indent=2)
    finally:
        db.close()


# ============================================
# Tool: Compare Techniques
# ============================================
@tool
def compare_techniques(technique_a: str, technique_b: str) -> str:
    """
    Compare two RAG techniques head-to-head across all metrics.

    Args:
        technique_a: First technique name
        technique_b: Second technique name

    Returns:
        JSON comparison showing which technique wins in each metric category.
    """
    db = next(get_db())
    try:
        def get_stats(technique):
            return db.query(
                func.avg(RAGMetric.latency_ms).label('avg_latency'),
                func.avg(RAGMetric.faithfulness).label('faithfulness'),
                func.avg(RAGMetric.answer_relevancy).label('relevancy'),
                func.avg(RAGMetric.context_precision).label('precision'),
                func.avg(RAGMetric.context_recall).label('recall'),
                func.count(RAGExecution.id).label('count'),
            ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id
            ).filter(RAGExecution.technique_name == technique
            ).first()

        stats_a = get_stats(technique_a)
        stats_b = get_stats(technique_b)

        if not stats_a.count or not stats_b.count:
            return json.dumps({"error": "One or both techniques have no data"})

        comparison = {
            "techniques": [technique_a, technique_b],
            "sample_sizes": [stats_a.count, stats_b.count],
            "metrics": {
                "latency_ms": {
                    technique_a: round(stats_a.avg_latency or 0, 2),
                    technique_b: round(stats_b.avg_latency or 0, 2),
                    "winner": technique_a if (stats_a.avg_latency or 999999) < (stats_b.avg_latency or 999999) else technique_b,
                    "difference_pct": round(abs((stats_a.avg_latency or 0) - (stats_b.avg_latency or 0)) / max(stats_a.avg_latency or 1, 1) * 100, 1),
                },
                "faithfulness": {
                    technique_a: round((stats_a.faithfulness or 0) * 100, 1),
                    technique_b: round((stats_b.faithfulness or 0) * 100, 1),
                    "winner": technique_a if (stats_a.faithfulness or 0) > (stats_b.faithfulness or 0) else technique_b,
                },
                "answer_relevancy": {
                    technique_a: round((stats_a.relevancy or 0) * 100, 1),
                    technique_b: round((stats_b.relevancy or 0) * 100, 1),
                    "winner": technique_a if (stats_a.relevancy or 0) > (stats_b.relevancy or 0) else technique_b,
                },
                "context_precision": {
                    technique_a: round((stats_a.precision or 0) * 100, 1),
                    technique_b: round((stats_b.precision or 0) * 100, 1),
                    "winner": technique_a if (stats_a.precision or 0) > (stats_b.precision or 0) else technique_b,
                },
                "context_recall": {
                    technique_a: round((stats_a.recall or 0) * 100, 1),
                    technique_b: round((stats_b.recall or 0) * 100, 1),
                    "winner": technique_a if (stats_a.recall or 0) > (stats_b.recall or 0) else technique_b,
                },
            }
        }

        # Count wins
        wins = {technique_a: 0, technique_b: 0}
        for metric, data in comparison["metrics"].items():
            wins[data["winner"]] += 1
        comparison["overall_winner"] = technique_a if wins[technique_a] > wins[technique_b] else technique_b
        comparison["win_count"] = wins

        return json.dumps(comparison, indent=2)
    finally:
        db.close()


# ============================================
# Tool: Get Best Technique
# ============================================
@tool
def get_best_technique(metric: str) -> str:
    """
    Find the best performing technique for a specific metric.

    Args:
        metric: One of 'latency', 'faithfulness', 'relevancy', 'precision', 'recall', 'overall'

    Returns:
        JSON with ranking of techniques for the specified metric.
    """
    db = next(get_db())
    try:
        metric_map = {
            'latency': (RAGMetric.latency_ms, 'asc'),  # Lower is better
            'faithfulness': (RAGMetric.faithfulness, 'desc'),
            'relevancy': (RAGMetric.answer_relevancy, 'desc'),
            'precision': (RAGMetric.context_precision, 'desc'),
            'recall': (RAGMetric.context_recall, 'desc'),
        }

        if metric == 'overall':
            # Calculate composite score
            results = db.query(
                RAGExecution.technique_name,
                func.count(RAGExecution.id).label('count'),
                func.avg(RAGMetric.faithfulness).label('faithfulness'),
                func.avg(RAGMetric.answer_relevancy).label('relevancy'),
                func.avg(RAGMetric.context_precision).label('precision'),
                func.avg(RAGMetric.context_recall).label('recall'),
                func.avg(RAGMetric.latency_ms).label('latency'),
            ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id
            ).group_by(RAGExecution.technique_name).all()

            rankings = []
            for r in results:
                # Composite: 40% quality, 30% relevancy, 20% precision/recall, 10% speed
                quality_score = (r.faithfulness or 0) * 0.4 + (r.relevancy or 0) * 0.3
                context_score = ((r.precision or 0) + (r.recall or 0)) / 2 * 0.2
                # Normalize latency (assume 5000ms is worst, 0 is best)
                speed_score = max(0, 1 - (r.latency or 5000) / 5000) * 0.1
                composite = quality_score + context_score + speed_score

                rankings.append({
                    "technique": r.technique_name,
                    "composite_score": round(composite * 100, 1),
                    "executions": r.count,
                })

            rankings.sort(key=lambda x: x["composite_score"], reverse=True)
            return json.dumps({"metric": "overall", "rankings": rankings}, indent=2)

        if metric not in metric_map:
            return json.dumps({"error": f"Invalid metric. Choose from: {list(metric_map.keys())} or 'overall'"})

        column, order = metric_map[metric]
        order_func = func.avg(column).asc() if order == 'asc' else func.avg(column).desc()

        results = db.query(
            RAGExecution.technique_name,
            func.avg(column).label('value'),
            func.count(RAGExecution.id).label('count'),
        ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id
        ).group_by(RAGExecution.technique_name
        ).order_by(order_func).all()

        rankings = []
        for i, r in enumerate(results, 1):
            value = r.value or 0
            if metric != 'latency':
                value = value * 100  # Convert to percentage
            rankings.append({
                "rank": i,
                "technique": r.technique_name,
                "value": round(value, 2),
                "unit": "ms" if metric == 'latency' else "%",
                "executions": r.count,
            })

        return json.dumps({"metric": metric, "rankings": rankings}, indent=2)
    finally:
        db.close()


# ============================================
# Tool: Get Execution Details
# ============================================
@tool
def get_execution_details(technique_name: str, limit: int = 5) -> str:
    """
    Get details of recent executions for a technique, including queries and answers.

    Args:
        technique_name: Name of the technique
        limit: Number of recent executions to retrieve (default 5, max 10)

    Returns:
        JSON with execution details including queries, answers, and metrics.
    """
    db = next(get_db())
    try:
        limit = min(limit, 10)  # Cap at 10

        results = db.query(RAGExecution).filter(
            RAGExecution.technique_name == technique_name
        ).order_by(desc(RAGExecution.created_at)).limit(limit).all()

        if not results:
            return json.dumps({"error": f"No executions found for '{technique_name}'"})

        executions = []
        for r in results:
            exec_data = {
                "id": r.id,
                "query": r.query_text[:200] + "..." if len(r.query_text) > 200 else r.query_text,
                "answer_preview": r.answer_text[:300] + "..." if len(r.answer_text) > 300 else r.answer_text,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "chunks_retrieved": len(r.sources) if r.sources else 0,
            }
            if r.metrics:
                exec_data["metrics"] = {
                    "latency_ms": round(r.metrics.latency_ms, 2),
                    "faithfulness": round((r.metrics.faithfulness or 0) * 100, 1),
                    "answer_relevancy": round((r.metrics.answer_relevancy or 0) * 100, 1),
                }
            executions.append(exec_data)

        return json.dumps({
            "technique": technique_name,
            "count": len(executions),
            "executions": executions
        }, indent=2)
    finally:
        db.close()


# ============================================
# Tool: Get Anomalies
# ============================================
@tool
def get_anomalies() -> str:
    """
    Detect performance anomalies and outliers across all techniques.

    Returns:
        JSON with identified anomalies such as high latency spikes,
        low quality scores, and inconsistent performance.
    """
    db = next(get_db())
    try:
        anomalies = []

        # Get all techniques
        techniques = db.query(RAGExecution.technique_name).distinct().all()

        for (technique,) in techniques:
            stats = db.query(
                func.avg(RAGMetric.latency_ms).label('avg_latency'),
                func.max(RAGMetric.latency_ms).label('max_latency'),
                func.min(RAGMetric.latency_ms).label('min_latency'),
                func.avg(RAGMetric.faithfulness).label('avg_faith'),
                func.min(RAGMetric.faithfulness).label('min_faith'),
                func.avg(RAGMetric.context_precision).label('avg_precision'),
                func.avg(RAGMetric.context_recall).label('avg_recall'),
                func.count(RAGExecution.id).label('count'),
            ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id
            ).filter(RAGExecution.technique_name == technique).first()

            if not stats.count:
                continue

            # Check for latency anomalies (max > 2x avg)
            if stats.max_latency and stats.avg_latency:
                if stats.max_latency > stats.avg_latency * 2:
                    anomalies.append({
                        "type": "latency_spike",
                        "technique": technique,
                        "severity": "high" if stats.max_latency > stats.avg_latency * 3 else "medium",
                        "details": f"Max latency ({stats.max_latency:.0f}ms) is {stats.max_latency/stats.avg_latency:.1f}x higher than average ({stats.avg_latency:.0f}ms)",
                    })

            # Check for high variance using range-based estimation
            if stats.max_latency and stats.min_latency and stats.avg_latency:
                range_ratio = (stats.max_latency - stats.min_latency) / stats.avg_latency
                if range_ratio > 1.0:  # Large spread relative to mean
                    anomalies.append({
                        "type": "high_variance",
                        "technique": technique,
                        "severity": "medium",
                        "details": f"High latency variance (range/avg={range_ratio:.2f}). Performance is inconsistent.",
                    })

            # Check for low faithfulness
            if stats.avg_faith is not None and stats.avg_faith < 0.5:
                anomalies.append({
                    "type": "low_faithfulness",
                    "technique": technique,
                    "severity": "high",
                    "details": f"Average faithfulness is only {stats.avg_faith*100:.1f}%. Answers may not be grounded in retrieved context.",
                })

            # Check for zero precision/recall
            if stats.avg_precision == 0 or stats.avg_recall == 0:
                anomalies.append({
                    "type": "zero_context_metrics",
                    "technique": technique,
                    "severity": "critical",
                    "details": f"Context precision ({stats.avg_precision*100:.0f}%) or recall ({stats.avg_recall*100:.0f}%) is zero. Check retrieval pipeline.",
                })

        if not anomalies:
            return json.dumps({"status": "healthy", "message": "No anomalies detected across all techniques."})

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        anomalies.sort(key=lambda x: severity_order.get(x["severity"], 99))

        return json.dumps({
            "status": "issues_found",
            "total_anomalies": len(anomalies),
            "anomalies": anomalies
        }, indent=2)
    finally:
        db.close()


# ============================================
# Tools List Export
# ============================================
TOOLS: List = [
    list_available_techniques,
    get_technique_stats,
    compare_techniques,
    get_best_technique,
    get_execution_details,
    get_anomalies,
]


def get_tools_info() -> list:
    """Get information about all available tools."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
        }
        for tool in TOOLS
    ]
