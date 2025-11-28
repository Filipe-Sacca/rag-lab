"""
Adaptive RAG - Intelligent RAG Technique Selection (Simplified)

Automatically routes queries to the optimal RAG technique
based on query classification.

4 Core Techniques:
┌─────────────┬─────────────────────────────────────────────┐
│ Category    │ Technique → Use Case                        │
├─────────────┼─────────────────────────────────────────────┤
│ simple      │ baseline  → Fast, factual queries (~60%)    │
│ complex     │ subquery  → Multi-part queries (~15%)       │
│ abstract    │ hyde      → Conceptual queries (~10%)       │
│ precision   │ reranking → High accuracy needs (~15%)      │
└─────────────┴─────────────────────────────────────────────┘

Usage:
    from techniques.adaptive import adaptive_rag

    result = await adaptive_rag("Compare Python and JavaScript")
    print(result["execution_details"]["technique_selected"])  # "subquery"
"""

from .orchestrator import run_adaptive_rag
from .prompts import (
    CATEGORY_TO_TECHNIQUE,
    TECHNIQUE_DESCRIPTIONS,
    VALID_CATEGORIES,
)
from .tools import (
    CORE_TECHNIQUES,
    OPTIONAL_TECHNIQUES,
    get_technique_function,
    get_core_technique_names,
)


async def adaptive_rag(
    query: str,
    top_k: int = 5,
    namespace: str | None = None,
) -> dict:
    """
    Adaptive RAG: Routes to optimal technique automatically.

    Categories & Techniques:
    - simple → baseline (fast, ~60% of queries)
    - complex → subquery (multi-part, ~15%)
    - abstract → hyde (conceptual, ~10%)
    - precision → reranking (accurate, ~15%)

    Args:
        query: User question
        top_k: Documents to retrieve (passed to technique)
        namespace: Pinecone namespace

    Returns:
        Dict with query, answer, sources, metrics, execution_details

    Example:
        >>> result = await adaptive_rag("O que é Python?")
        >>> result["execution_details"]["technique_selected"]
        'baseline'

        >>> result = await adaptive_rag("Compare Python e Java")
        >>> result["execution_details"]["technique_selected"]
        'subquery'
    """
    return await run_adaptive_rag(query=query, namespace=namespace)


__all__ = [
    "adaptive_rag",
    "run_adaptive_rag",
    "CATEGORY_TO_TECHNIQUE",
    "TECHNIQUE_DESCRIPTIONS",
    "VALID_CATEGORIES",
    "CORE_TECHNIQUES",
    "OPTIONAL_TECHNIQUES",
    "get_technique_function",
    "get_core_technique_names",
]
