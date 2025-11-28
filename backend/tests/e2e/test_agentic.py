"""
Teste Agentic RAG
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from techniques.agentic_rag import agentic_rag


if __name__ == "__main__":
    print("🚀 Testando Agentic RAG...\n")

    # Teste 1: Pergunta sobre HyDE
    result = agentic_rag(
        "O que é HyDE RAG e quando usar?",
        params={"default_technique": "baseline"},
    )

    print(f"{'='*60}")
    print("AGENTIC RAG - Teste")
    print(f"{'='*60}")
    print(f"Query: {result['query']}")
    print(f"\nAnswer: {result['answer'][:200]}...")
    print(f"\nTechnique: {result['execution_details']['technique_used']}")
    print(f"Iterations: {result['metrics'].get('total_iterations', 0)}")
    print(f"Latency: {result['metrics'].get('agent_latency_ms', 0):.0f}ms")
    print(f"\nSources: {len(result['sources'])} documentos")
