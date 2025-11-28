"""
Adaptive RAG - Orchestrator Module (Simplified - 4 Essential Techniques)

LangGraph-based orchestration for intelligent RAG technique selection.
Simplified to 4 core techniques for better classification accuracy.

Flow: Query → Classify → Select → Execute → Response
"""

import time
from typing import Dict, Any, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from core.llm import get_llm
from config import settings

from .prompts import (
    CLASSIFICATION_PROMPT,
    CATEGORY_TO_TECHNIQUE,
    DEFAULT_TECHNIQUE,
    VALID_CATEGORIES,
    get_routing_reason,
)
from .tools import (
    CORE_TECHNIQUES,
    execute_rag_technique,
    get_technique_function,
)


# ============================================
# State Definition
# ============================================
class AdaptiveState(TypedDict):
    """State maintained during adaptive RAG execution."""
    query: str
    query_type: str
    technique: str
    confidence: float
    answer: str
    sources: List[Dict]
    metrics: Dict[str, Any]
    execution_details: Dict[str, Any]


# ============================================
# Graph Nodes
# ============================================
def classify_query_node(state: AdaptiveState) -> AdaptiveState:
    """
    Node: Classify query into one of 4 categories.

    Categories: simple, complex, abstract, precision
    """
    query = state["query"]
    llm = get_llm(temperature=0.0, max_output_tokens=20)

    prompt = CLASSIFICATION_PROMPT.format(query=query)

    try:
        response = llm.invoke(prompt)
        classification = response.content.strip().lower()

        # Clean up response (remove punctuation, extra text)
        classification = classification.split()[0] if classification else "simple"
        classification = ''.join(c for c in classification if c.isalpha())

        # Validate classification
        if classification not in VALID_CATEGORIES:
            # Try to find valid category in response
            for cat in VALID_CATEGORIES:
                if cat in classification:
                    classification = cat
                    break
            else:
                classification = "simple"  # Safe fallback

        state["query_type"] = classification
        state["confidence"] = 0.90  # Higher confidence with fewer categories

    except Exception as e:
        print(f"Classification failed: {e}")
        state["query_type"] = "simple"
        state["confidence"] = 0.5

    return state


def select_technique_node(state: AdaptiveState) -> AdaptiveState:
    """
    Node: Map query category to RAG technique.
    """
    query_type = state["query_type"]
    technique = CATEGORY_TO_TECHNIQUE.get(query_type, DEFAULT_TECHNIQUE)
    state["technique"] = technique
    return state


def execute_rag_node(state: AdaptiveState) -> AdaptiveState:
    """
    Node: Execute the selected RAG technique.
    """
    query = state["query"]
    technique = state["technique"]

    rag_func = get_technique_function(technique)

    try:
        # Build kwargs based on technique
        kwargs = {}
        if technique == "reranking":
            kwargs["cohere_api_key"] = settings.COHERE_API_KEY
        elif technique == "subquery":
            kwargs["top_k_per_subquery"] = 5

        # Execute
        result = execute_rag_technique(rag_func, query, **kwargs)

        state["answer"] = result.get("answer", "")
        state["sources"] = result.get("sources", [])
        state["metrics"] = result.get("metrics", {})

    except Exception as e:
        print(f"RAG execution failed: {e}")
        state["answer"] = f"Erro ao executar técnica {technique}: {str(e)}"
        state["sources"] = []
        state["metrics"] = {}

    return state


def build_response_node(state: AdaptiveState) -> AdaptiveState:
    """
    Node: Build final response with execution details.
    """
    state["execution_details"] = {
        "query_type": state["query_type"],
        "technique_selected": state["technique"],
        "confidence": state["confidence"],
        "routing_reason": get_routing_reason(state["query_type"]),
        "available_techniques": list(CORE_TECHNIQUES.keys()),
    }
    return state


# ============================================
# Graph Construction
# ============================================
def create_adaptive_graph() -> StateGraph:
    """
    Create the simplified adaptive RAG graph.

    Flow: START → classify → select → execute → build → END
    """
    workflow = StateGraph(AdaptiveState)

    # Add nodes
    workflow.add_node("classify", classify_query_node)
    workflow.add_node("select", select_technique_node)
    workflow.add_node("execute", execute_rag_node)
    workflow.add_node("build", build_response_node)

    # Linear flow
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "select")
    workflow.add_edge("select", "execute")
    workflow.add_edge("execute", "build")
    workflow.add_edge("build", END)

    return workflow.compile()


# ============================================
# Main Execution Function
# ============================================
async def run_adaptive_rag(
    query: str,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """
    Execute simplified adaptive RAG pipeline.

    Routes to one of 4 core techniques:
    - baseline: Simple queries
    - reranking: Precision queries
    - subquery: Complex queries
    - hyde: Abstract queries

    Args:
        query: User question
        namespace: Pinecone namespace (optional)

    Returns:
        Dict with query, answer, sources, metrics, execution_details
    """
    start_time = time.time()

    # Create graph
    graph = create_adaptive_graph()

    # Initial state
    initial_state: AdaptiveState = {
        "query": query,
        "query_type": "",
        "technique": "",
        "confidence": 0.0,
        "answer": "",
        "sources": [],
        "metrics": {},
        "execution_details": {},
    }

    # Execute graph
    final_state = graph.invoke(initial_state)

    # Calculate metrics
    total_latency_ms = (time.time() - start_time) * 1000

    technique_metrics = final_state.get("metrics", {})

    combined_metrics = {
        **technique_metrics,
        "adaptive_latency_ms": round(total_latency_ms, 2),
        "technique": "adaptive_rag",
        "selected_technique": final_state["technique"],
        "query_classification": final_state["query_type"],
        "routing_confidence": final_state["confidence"],
    }

    return {
        "query": query,
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "metrics": combined_metrics,
        "execution_details": {
            **final_state["execution_details"],
            "technique_metrics": technique_metrics,
        },
    }
