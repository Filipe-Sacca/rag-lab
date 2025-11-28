"""
Agentic RAG - Entry Point

Este arquivo é mantido para compatibilidade com imports existentes.
A implementação real está no módulo agentic/.

Estrutura modular:
- agentic/tools.py: Ferramentas com @tool decorator
- agentic/prompts.py: System prompts
- agentic/orchestrator.py: LangGraph workflow
- agentic/__init__.py: Interface pública

Migração:
Antes: from techniques.agentic_rag import agentic_rag
Depois: from techniques.agentic import agentic_rag
"""

from typing import Dict, Any

# Import da implementação modular
from .agentic import agentic_rag as _agentic_rag
from .agentic import AGENTIC_TOOLS, get_system_prompt


# ============================================
# Interface Pública (Wrapper)
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
            - max_iterations: Máximo de loops ReAct

    Returns:
        Dict com:
        - query: Pergunta original
        - answer: Resposta gerada
        - sources: Documentos usados
        - metrics: Métricas de execução
        - execution_details: Detalhes do agente

    Note:
        Esta é uma função wrapper. A implementação real está em:
        techniques.agentic.agentic_rag()
    """
    return _agentic_rag(query=query, params=params, namespace=namespace)


# ============================================
# Testes Rápidos
# ============================================

if __name__ == "__main__":
    # Teste básico
    result = agentic_rag(
        "O que é HyDE RAG?",
        params={"default_technique": "baseline"},
    )

    print(f"\n{'='*60}")
    print("AGENTIC RAG - Teste")
    print(f"{'='*60}")
    print(f"Query: {result['query']}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nTechnique: {result['execution_details']['technique_used']}")
    print(f"Iterations: {result['metrics']['total_iterations']}")
    print(f"Latency: {result['metrics']['agent_latency_ms']:.0f}ms")
    print(f"\nSources: {len(result['sources'])} documentos")
