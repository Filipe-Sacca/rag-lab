"""
RAG Analyst Agent - Intelligent RAG Performance Analysis

LangGraph-powered agent that analyzes RAG technique performance
using database queries and provides actionable insights.

Architecture:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Question   │────▶│    Agent     │────▶│   Analysis   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
              ┌──────────┐   ┌──────────┐
              │  Tools   │   │   LLM    │
              └──────────┘   └──────────┘
                    │
                    ▼
              ┌──────────┐
              │ Database │
              └──────────┘

Tools Available:
┌─────────────────────────┬───────────────────────────────────────┐
│ Tool                    │ Function                              │
├─────────────────────────┼───────────────────────────────────────┤
│ list_available_techniques│ List techniques with execution counts │
│ get_technique_stats     │ Detailed stats for one technique      │
│ compare_techniques      │ Head-to-head comparison (A vs B)      │
│ get_best_technique      │ Best technique for a metric           │
│ get_execution_details   │ Recent executions + queries           │
│ get_anomalies           │ Detect performance problems           │
└─────────────────────────┴───────────────────────────────────────┘

Usage:
    from agents.rag_analyst import run_analyst

    result = await run_analyst("Qual técnica tem melhor performance?")
    print(result["response"])
    print(f"Tools used: {len(result['tool_calls'])}")
"""

from .orchestrator import run_analyst, create_analyst_graph
from .tools import (
    TOOLS,
    get_tools_info,
    list_available_techniques,
    get_technique_stats,
    compare_techniques,
    get_best_technique,
    get_execution_details,
    get_anomalies,
)
from .prompts import (
    SYSTEM_PROMPT,
    METRIC_DESCRIPTIONS,
    ANALYSIS_TEMPLATE,
    COMPARISON_TEMPLATE,
    get_metric_emoji,
    get_metric_direction,
)


__all__ = [
    # Main functions
    "run_analyst",
    "create_analyst_graph",
    # Tools
    "TOOLS",
    "get_tools_info",
    "list_available_techniques",
    "get_technique_stats",
    "compare_techniques",
    "get_best_technique",
    "get_execution_details",
    "get_anomalies",
    # Prompts
    "SYSTEM_PROMPT",
    "METRIC_DESCRIPTIONS",
    "ANALYSIS_TEMPLATE",
    "COMPARISON_TEMPLATE",
    "get_metric_emoji",
    "get_metric_direction",
]
