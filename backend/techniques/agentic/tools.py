"""
Agentic RAG - Ferramentas (@tool decorated)

Ferramentas que o agente LLM pode escolher usar:
- internal_rag_tool: Busca na base vetorial interna
- web_search_tool: Busca informações na web
"""

import asyncio
import inspect
from typing import Dict, Any

from langchain_core.tools import tool

# Imports relativos ou absolutos dependendo do contexto
try:
    from ..baseline_rag import baseline_rag
    from ..hyde_rag import hyde_rag
    from ..reranking_rag import reranking_rag
except ImportError:
    from techniques.baseline_rag import baseline_rag
    from techniques.hyde_rag import hyde_rag
    from techniques.reranking_rag import reranking_rag


# ============================================
# Ferramentas Disponíveis para o Agente
# ============================================

@tool
def internal_rag_tool(query: str, technique: str = "baseline") -> Dict[str, Any]:
    """
    Busca informações na base vetorial interna usando RAG.

    Args:
        query: Pergunta do usuário
        technique: Técnica RAG a usar (baseline, hyde, reranking)

    Returns:
        Dict com answer, sources, metrics
    """
    technique_map = {
        "baseline": baseline_rag,
        "hyde": hyde_rag,
        "reranking": reranking_rag,
    }

    rag_func = technique_map.get(technique, baseline_rag)

    # Se função é async, roda com asyncio
    if inspect.iscoroutinefunction(rag_func):
        result = asyncio.run(rag_func(query))
    else:
        result = rag_func(query)

    # Propagate RAGAS scores from underlying technique
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "technique_used": technique,
        "metrics": result["metrics"],  # Already includes RAGAS scores
    }


@tool
def web_search_tool(query: str) -> Dict[str, Any]:
    """
    Busca informações na web quando base interna não tem dados.

    Args:
        query: Pergunta para buscar na web

    Returns:
        Dict com resultados da web
    """
    # TODO: Implementar integração com API de busca (Tavily, SerpAPI, etc)
    return {
        "answer": f"[Web Search não implementado ainda] Query: {query}",
        "sources": [],
        "technique_used": "web_search",
    }


# ============================================
# Lista de Ferramentas (para fácil importação)
# ============================================
AGENTIC_TOOLS = [internal_rag_tool, web_search_tool]
