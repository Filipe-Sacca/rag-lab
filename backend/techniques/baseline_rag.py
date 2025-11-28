"""
Baseline RAG - Traditional RAG Implementation

Simple and direct Retrieval-Augmented Generation pipeline:
1. Embed query with text-embedding-004
2. Search in Pinecone (top_k=5)
3. Retrieve relevant chunks
4. Generate response with Gemini 2.5 Flash

This is the foundation technique for comparison with all others.
"""

import time
from typing import Dict, List, Any

from langchain_core.documents import Document

from core.llm import smart_invoke
from core.embeddings import get_query_embedding_model
from core.vector_store import get_vector_store
from core.prompts import get_answer_prompt  # ← NOVO: Prompt centralizado
from config import settings
from evaluation.ragas_eval import evaluate_rag_response


async def baseline_rag(
    query: str,
    top_k: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 500,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """
    Baseline RAG: Traditional embed -> search -> generate pipeline

    This is the simplest RAG implementation without optimizations.
    Serves as baseline for comparing all advanced techniques.

    Pipeline:
        1. Generate query embedding
        2. Search Pinecone for top-k similar chunks
        3. Build prompt with retrieved context
        4. Generate answer with Gemini

    Args:
        query: User question
        top_k: Number of chunks to retrieve (default: 5)
        temperature: LLM temperature for generation (default: 0.7)
        max_tokens: Maximum tokens in response (default: 500)

    Returns:
        Dict containing:
            - answer: Generated response from LLM
            - sources: List of retrieved chunks with metadata and scores
            - metrics: Performance metrics (latency, tokens, cost)
            - execution_details: Step-by-step execution information

    Example:
        >>> result = await baseline_rag("Qual foi o lucro do Q3?")
        >>> print(result["answer"])
        >>> print(f"Latency: {result['metrics']['latency_ms']}ms")
    """
    start_time = time.time()
    execution_details = {
        "technique": "baseline_rag",
        "steps": []
    }

    # Step 1: Initialize components
    step_start = time.time()
    embeddings = get_query_embedding_model()
    vector_store = get_vector_store(namespace=namespace)

    execution_details["steps"].append({
        "step": "initialization",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "components": ["embeddings", "vector_store"]
    })

    # Step 2: Embed query
    step_start = time.time()
    query_vector = embeddings.embed_query(query)

    execution_details["steps"].append({
        "step": "embed_query",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "vector_dimension": len(query_vector)
    })

    # Step 3: Search Pinecone
    step_start = time.time()
    retrieved_docs: List[Document] = vector_store.similarity_search_with_score(
        query,
        k=top_k
    )

    execution_details["steps"].append({
        "step": "similarity_search",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "chunks_retrieved": len(retrieved_docs),
        "top_k": top_k
    })

    # Step 4: Build context from retrieved chunks
    step_start = time.time()
    sources = []
    context_parts = []

    for doc, score in retrieved_docs:
        sources.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })
        context_parts.append(doc.page_content)

    context = "\n\n".join(context_parts)

    execution_details["steps"].append({
        "step": "build_context",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "context_length_chars": len(context)
    })

    # Step 5: Build prompt (usando PromptTemplate centralizado)
    answer_prompt = get_answer_prompt('baseline')  # Mesmo prompt usado por todas as técnicas
    prompt = answer_prompt.format(context=context, query=query)

    # Step 6: Generate answer with LLM (smart: Live API first, fallback to Standard)
    step_start = time.time()
    answer, api_type = await smart_invoke(
        prompt,
        temperature=temperature,
        max_output_tokens=max_tokens
    )

    generation_duration = round((time.time() - step_start) * 1000, 2)

    execution_details["steps"].append({
        "step": "llm_generation",
        "duration_ms": generation_duration,
        "model": settings.GEMINI_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "api_type": api_type  # "live" or "standard"
    })

    # Calculate total metrics
    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    # Token counting (approximation)
    input_tokens = _estimate_tokens(prompt)
    output_tokens = _estimate_tokens(answer)
    total_tokens = input_tokens + output_tokens

    # Cost estimation (Gemini 1.5 Flash pricing)
    # Input: $0.00001875 / 1K tokens, Output: $0.000075 / 1K tokens
    input_cost = (input_tokens / 1000) * 0.00001875
    output_cost = (output_tokens / 1000) * 0.000075
    total_cost = input_cost + output_cost

    # RAGAS Evaluation
    try:
        contexts = [doc.page_content for doc, _ in retrieved_docs]
        ragas_scores = await evaluate_rag_response(
            query=query,
            answer=answer,
            contexts=contexts,
            ground_truth=None
        )
    except Exception as e:
        print(f"Warning: RAGAS evaluation failed: {e}")
        ragas_scores = {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": None,
            "context_recall": None,
        }

    metrics = {
        "latency_ms": total_latency_ms,
        "latency_seconds": round(total_latency_ms / 1000, 2),
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_tokens
        },
        "cost": {
            "input_usd": round(input_cost, 6),
            "output_usd": round(output_cost, 6),
            "total_usd": round(total_cost, 6)
        },
        "chunks_retrieved": len(retrieved_docs),
        "technique": "baseline_rag",
        # RAGAS metrics
        "faithfulness": ragas_scores.get("faithfulness", 0.0),
        "answer_relevancy": ragas_scores.get("answer_relevancy", 0.0),
        "context_precision": ragas_scores.get("context_precision"),
        "context_recall": ragas_scores.get("context_recall"),
    }

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "metrics": metrics,
        "execution_details": execution_details
    }


# NOTA: Função _build_prompt() REMOVIDA!
# Agora usamos get_answer_prompt() de core.prompts
# Isso garante que todas as técnicas RAG usem o MESMO prompt para comparação justa.
#
# Código antigo (DEPRECATED):
# def _build_prompt(query: str, context: str) -> str:
#     return f"""Voce e um assistente..."""
#
# Código novo (linha 127-128):
# answer_prompt = get_answer_prompt('baseline')
# prompt = answer_prompt.format(context=context, query=query)


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses simple approximation: ~4 characters per token for Portuguese.
    This is conservative and works well for cost estimation.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Conservative estimate: 4 chars per token
    return len(text) // 4


def retrieve_only(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Only retrieve chunks without generation.

    Useful for debugging and testing retrieval quality.

    Args:
        query: User question
        top_k: Number of chunks to retrieve

    Returns:
        List of retrieved chunks with scores
    """
    vector_store = get_vector_store()
    retrieved_docs = vector_store.similarity_search_with_score(query, k=top_k)

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        }
        for doc, score in retrieved_docs
    ]
