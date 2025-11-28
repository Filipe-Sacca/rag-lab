"""
Agentic RAG Module

Módulo modular para Agentic RAG:
- tools.py: Ferramentas com @tool decorator
- prompts.py: System prompts
- orchestrator.py: LangGraph workflow

Interface pública:
- agentic_rag(query, params): Função principal
"""

import time
from typing import Dict, Any

from .orchestrator import create_agent_graph, create_initial_state
from .tools import AGENTIC_TOOLS
from .prompts import get_system_prompt


# ============================================
# Interface Pública
# ============================================

def agentic_rag(
    query: str,
    params: Dict[str, Any] = None,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """
    Executa Agentic RAG com LangGraph.

    Agent decide:
    - Se precisa usar RAG
    - Qual técnica RAG usar
    - Se precisa buscar na web

    Args:
        query: Pergunta do usuário
        params: Parâmetros opcionais
            - default_technique: baseline|hyde|reranking
            - max_iterations: Máximo de loops ReAct (padrão: 10)
            - prompt_version: system|concise|verbose (padrão: system)
        namespace: Namespace opcional (não usado atualmente)

    Returns:
        Dict com:
        - query: Pergunta original
        - answer: Resposta gerada
        - sources: Documentos usados
        - metrics: Métricas de execução
        - execution_details: Detalhes do agente
    """
    params = params or {}
    start_time = time.time()

    # Cria grafo
    graph = create_agent_graph()

    # Cria estado inicial
    initial_state = create_initial_state(query, params)

    # Executa grafo
    final_state = graph.invoke(
        initial_state,
        config={"recursion_limit": params.get("max_iterations", 10)},
    )

    # Calcula métricas
    latency_ms = (time.time() - start_time) * 1000

    # Combina metrics
    combined_metrics = {
        **final_state.get("metrics", {}),
        "agent_latency_ms": latency_ms,
        "total_iterations": final_state["execution_details"].get("total_messages", 0) // 2,
    }

    return {
        "query": query,
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "metrics": combined_metrics,
        "execution_details": {
            **final_state["execution_details"],
            "params": params,
        },
    }


# ============================================
# Exports
# ============================================

__all__ = [
    "agentic_rag",
    "AGENTIC_TOOLS",
    "get_system_prompt",
    "create_agent_graph",
    "create_initial_state",
]
