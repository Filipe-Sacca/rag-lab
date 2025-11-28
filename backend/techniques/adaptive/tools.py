"""
Adaptive RAG - Tools Module (Simplified - 4 Essential Techniques)

Each essential RAG technique wrapped as a callable.
Focused on the 4 core techniques that cover 95%+ of use cases.

Core Techniques:
- baseline: Simple queries (fast, cheap)
- reranking: High precision (accurate)
- subquery: Complex queries (comprehensive)
- hyde: Abstract queries (conceptual)
"""

import asyncio
import inspect
from typing import Dict, Any, Callable

# Import essential RAG techniques
from techniques.baseline_rag import baseline_rag
from techniques.hyde_rag import hyde_rag
from techniques.reranking_rag import reranking_rag
from techniques.subquery import subquery_rag

# Optional: Keep imports for manual use (not in router)
from techniques.fusion import fusion_rag
from techniques.graph_rag import graph_rag


# ============================================
# Helper: Run async function safely
# ============================================
def run_async_safely(coro):
    """Run async coroutine safely, handling existing event loops."""
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


def execute_rag_technique(func: Callable, query: str, **kwargs) -> Dict[str, Any]:
    """Execute a RAG technique function, handling async/sync."""
    if inspect.iscoroutinefunction(func):
        return run_async_safely(func(query, **kwargs))
    return func(query, **kwargs)


# ============================================
# Core Technique Functions (4 Essential)
# ============================================
CORE_TECHNIQUES = {
    "baseline": baseline_rag,
    "reranking": reranking_rag,
    "subquery": subquery_rag,
    "hyde": hyde_rag,
}

# Optional techniques (available but not in auto-router)
OPTIONAL_TECHNIQUES = {
    "fusion": fusion_rag,
    "graph": graph_rag,
}

# All techniques combined
ALL_TECHNIQUES = {**CORE_TECHNIQUES, **OPTIONAL_TECHNIQUES}


def get_technique_function(name: str) -> Callable:
    """Get technique function by name."""
    return ALL_TECHNIQUES.get(name, baseline_rag)


def get_core_technique_names() -> list:
    """Get list of core technique names."""
    return list(CORE_TECHNIQUES.keys())


def is_core_technique(name: str) -> bool:
    """Check if technique is a core technique."""
    return name in CORE_TECHNIQUES
