"""
RAG Techniques Module

Collection of 7 RAG techniques for comparison and testing:
1. Baseline RAG - Traditional RAG (embed → search → generate)
2. HyDE RAG - Hypothetical Document Embeddings
3. Reranking RAG - Two-stage retrieval with cross-encoder
4. Agentic RAG - Agent-based with LangGraph (autonomous)
5. Fusion RAG - Multi-query with Reciprocal Rank Fusion
6. Sub-Query RAG - Query decomposition for complex questions
7. Graph RAG - Knowledge graph enhanced retrieval
"""

from techniques.baseline_rag import baseline_rag, retrieve_only
from techniques.hyde_rag import hyde_rag
from techniques.reranking_rag import reranking_rag
from techniques.agentic_rag import agentic_rag
from techniques.fusion import fusion_rag
from techniques.subquery import subquery_rag
from techniques.graph_rag import graph_rag

__all__ = [
    # Core techniques
    "baseline_rag",
    "retrieve_only",
    "hyde_rag",
    "reranking_rag",
    "agentic_rag",
    # Advanced techniques
    "fusion_rag",
    "subquery_rag",
    "graph_rag",
]
