"""
Analytics API Routes

Endpoints for RAG technique comparison and analysis.
Includes both simple aggregations and LangGraph-powered intelligent agent.
"""

import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.database import get_db
from services.analytics import get_aggregated_stats, get_rankings, get_full_analysis
from services.analysis import (
    save_analysis,
    get_analysis_by_id,
    list_analyses,
    delete_analysis,
    get_analyses_summary,
)
from agents.rag_analyst import TOOLS as ANALYST_TOOLS, run_analyst, get_tools_info

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class AgentQueryRequest(BaseModel):
    """Request model for agent queries."""
    question: str = Field(
        ...,
        description="Question about RAG technique performance",
        min_length=5,
        max_length=1000,
        examples=[
            "Qual técnica tem melhor performance geral?",
            "Compare reranking vs baseline",
            "Existem anomalias de performance?",
        ]
    )
    max_iterations: Optional[int] = Field(
        default=10,
        description="Maximum tool call iterations",
        ge=1,
        le=20
    )


class AgentQueryResponse(BaseModel):
    """Response model for agent queries."""
    id: Optional[int] = None  # Analysis ID (if saved)
    response: str
    tool_calls: list
    iterations: int
    duration_ms: Optional[float] = None


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get aggregated statistics for all techniques.

    Returns:
        Aggregated stats per technique
    """
    try:
        stats = get_aggregated_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        ) from e


@router.get("/rankings")
async def get_technique_rankings(db: Session = Depends(get_db)):
    """
    Get rankings for each metric.

    Returns:
        Rankings per metric
    """
    try:
        stats = get_aggregated_stats(db)
        rankings = get_rankings(stats)
        return rankings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rankings: {str(e)}"
        ) from e


@router.post("/analyze")
async def analyze_techniques(db: Session = Depends(get_db)):
    """
    Generate full comparative analysis with LLM insights.

    This endpoint aggregates all execution data, calculates rankings,
    and uses Gemini to generate a comprehensive analysis.
    The analysis is automatically saved to the database for historical lookup.

    Returns:
        Complete analysis with stats, rankings, and LLM insights
    """
    try:
        start_time = time.time()
        analysis = await get_full_analysis(db)
        duration_ms = (time.time() - start_time) * 1000

        # Auto-save analysis to database with full structured data
        save_analysis(
            db=db,
            question="Análise comparativa completa das técnicas RAG",
            response=analysis.get("llm_analysis", ""),
            tool_calls=[{"tool": "get_full_analysis", "result_preview": "Aggregated stats + rankings"}],
            iterations=1,
            duration_ms=duration_ms,
            analysis_data={
                "aggregated_data": analysis.get("aggregated_data"),
                "rankings": analysis.get("rankings"),
            },
        )

        return analysis
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analysis: {str(e)}"
        ) from e


# =============================================================================
# LANGGRAPH AGENT ENDPOINT
# =============================================================================

@router.post("/agent", response_model=AgentQueryResponse)
async def query_analyst_agent(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Query the RAG Analyst Agent with a natural language question.

    This endpoint uses a LangGraph-powered agent that can:
    - Query the database dynamically using tools
    - Compare techniques head-to-head
    - Detect anomalies and performance issues
    - Provide actionable recommendations

    The analysis is automatically saved to the database for historical lookup.

    Example questions:
    - "Qual técnica tem melhor performance geral?"
    - "Compare reranking vs baseline"
    - "Existem anomalias de performance?"
    - "Me mostre as últimas execuções do hyde"

    Returns:
        Agent response with analysis, list of tools used, iteration count, and analysis ID
    """
    try:
        start_time = time.time()

        result = await run_analyst(
            question=request.question,
            max_iterations=request.max_iterations
        )

        duration_ms = (time.time() - start_time) * 1000

        # Auto-save analysis to database
        analysis = save_analysis(
            db=db,
            question=request.question,
            response=result["response"],
            tool_calls=result["tool_calls"],
            iterations=result["iterations"],
            duration_ms=duration_ms,
        )

        return AgentQueryResponse(
            id=analysis.id,
            response=result["response"],
            tool_calls=result["tool_calls"],
            iterations=result["iterations"],
            duration_ms=round(duration_ms, 2),
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent module not available: {str(e)}"
        ) from e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent query failed: {str(e)}"
        ) from e


@router.get("/agent/tools")
async def list_agent_tools():
    """
    List all tools available to the RAG Analyst Agent.

    Returns:
        List of tool names and descriptions
    """
    tools_info = get_tools_info()
    return {
        "total_tools": len(tools_info),
        "tools": tools_info,
    }


# =============================================================================
# ANALYSIS HISTORY ENDPOINTS
# =============================================================================

@router.get("/analyses")
async def get_analyses(
    db: Session = Depends(get_db),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    limit: int = Query(50, ge=1, le=100, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """
    List saved analyses with optional timestamp filtering.

    Query Parameters:
    - date_from: Filter analyses from this date (ISO format, e.g., 2024-01-01T00:00:00)
    - date_to: Filter analyses until this date (ISO format)
    - limit: Maximum results (default 50, max 100)
    - offset: Skip N results for pagination

    Returns:
        List of analyses with total count
    """
    try:
        result = list_analyses(
            db=db,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        ) from e


@router.get("/analyses/summary")
async def get_analysis_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics of all saved analyses.

    Returns:
        Summary with total count, average iterations, and date range
    """
    try:
        return get_analyses_summary(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        ) from e


@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get a specific analysis by ID.

    Returns:
        Analysis details
    """
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    return analysis.to_dict()


@router.delete("/analyses/{analysis_id}")
async def remove_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific analysis by ID.

    Returns:
        Success message
    """
    deleted = delete_analysis(db, analysis_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    return {"message": f"Analysis {analysis_id} deleted successfully"}
