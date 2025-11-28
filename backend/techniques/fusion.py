"""
RAG Fusion - Multi-Query Retrieval with Reciprocal Rank Fusion

Advanced RAG technique that improves retrieval through:
1. Generate multiple query variations (3-5 paraphrases)
2. Search with each query variation independently
3. Combine results using Reciprocal Rank Fusion (RRF)
4. Generate answer from fused context

Key Improvement vs Baseline:
- Context Recall: +40% (captures diverse relevant docs)
- Robustness: Less sensitive to query phrasing
- Coverage: Retrieves documents that match different aspects

RRF Formula: score(doc) = Sum 1/(k + rank_i) for each list where doc appears
Where k=60 (constant), rank_i is position in list i
"""

import time
from typing import Dict, List, Any, Set
from collections import defaultdict

from langchain_core.documents import Document

from core.llm import smart_invoke, ainvoke_smart
from core.embeddings import get_query_embedding_model
from core.vector_store import get_vector_store
from core.prompts import get_answer_prompt
from config import settings
from evaluation.ragas_eval import evaluate_rag_response


async def fusion_rag(
    query: str,
    num_queries: int = 3,
    top_k_per_query: int = 10,
    final_top_k: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 500,
    rrf_k: int = 60,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """RAG Fusion: Multi-query retrieval with Reciprocal Rank Fusion"""
    start_time = time.time()
    execution_details = {"technique": "fusion_rag", "steps": []}

    # Initialize
    step_start = time.time()
    embeddings = get_query_embedding_model()
    vector_store = get_vector_store(namespace=namespace)

    execution_details["steps"].append({
        "step": "initialization",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "components": ["embeddings", "vector_store"]
    })

    # Generate query variations
    step_start = time.time()
    query_variations = await _generate_query_variations(query, num_queries)

    execution_details["steps"].append({
        "step": "generate_query_variations",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "num_variations": len(query_variations)
    })
    execution_details["query_variations"] = query_variations

    # Multi-query search
    step_start = time.time()
    all_results = []
    for q in query_variations:
        docs = vector_store.similarity_search_with_score(q, k=top_k_per_query)
        all_results.append(docs)

    execution_details["steps"].append({
        "step": "multi_query_search",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "num_queries": len(query_variations),
        "docs_per_query": top_k_per_query,
        "total_docs_retrieved": sum(len(docs) for docs in all_results)
    })

    # RRF fusion
    step_start = time.time()
    fused_docs = _reciprocal_rank_fusion(all_results, rrf_k, final_top_k)

    execution_details["steps"].append({
        "step": "reciprocal_rank_fusion",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "rrf_k": rrf_k,
        "final_docs_after_fusion": len(fused_docs)
    })

    # Build context
    sources = []
    context_parts = []
    for doc, rrf_score, original_scores in fused_docs:
        sources.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "rrf_score": float(rrf_score),
            "original_scores": [float(s) for s in original_scores]
        })
        context_parts.append(doc.page_content)

    context = "\n\n".join(context_parts)

    # Build prompt
    answer_prompt = get_answer_prompt('fusion')
    prompt = answer_prompt.format(context=context, query=query)

    # Generate answer (smart: Live API first, fallback to Standard)
    step_start = time.time()
    answer, api_type = await smart_invoke(
        prompt,
        temperature=temperature,
        max_output_tokens=max_tokens
    )

    execution_details["steps"].append({
        "step": "llm_generation",
        "duration_ms": round((time.time() - step_start) * 1000, 2),
        "model": settings.GEMINI_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "api_type": api_type
    })

    # Metrics
    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    input_tokens = len(prompt) // 4
    output_tokens = len(answer) // 4
    total_tokens = input_tokens + output_tokens

    input_cost = (input_tokens / 1000) * 0.00001875
    output_cost = (output_tokens / 1000) * 0.000075
    total_cost = input_cost + output_cost

    # RAGAS
    try:
        contexts = [source["content"] for source in sources]
        ragas_scores = await evaluate_rag_response(query=query, answer=answer, contexts=contexts, ground_truth=None)
    except Exception as e:
        print(f"Warning: RAGAS evaluation failed: {e}")
        ragas_scores = {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": None, "context_recall": None}

    metrics = {
        "latency_ms": total_latency_ms,
        "latency_seconds": round(total_latency_ms / 1000, 2),
        "tokens": {"input": input_tokens, "output": output_tokens, "total": total_tokens},
        "cost": {"input_usd": round(input_cost, 6), "output_usd": round(output_cost, 6), "total_usd": round(total_cost, 6)},
        "fusion_stats": {"num_query_variations": len(query_variations), "docs_per_query": top_k_per_query, "final_docs": len(fused_docs)},
        "chunks_retrieved": len(fused_docs),
        "technique": "fusion_rag",
        "faithfulness": ragas_scores.get("faithfulness", 0.0),
        "answer_relevancy": ragas_scores.get("answer_relevancy", 0.0),
        "context_precision": ragas_scores.get("context_precision"),
        "context_recall": ragas_scores.get("context_recall"),
    }

    return {"query": query, "answer": answer, "sources": sources, "metrics": metrics, "execution_details": execution_details}


async def _generate_query_variations(query: str, num_variations: int) -> List[str]:
    """Generate query variations using Live API"""
    prompt = f"""Gere {num_variations - 1} parafrases DIFERENTES da seguinte pergunta.

PERGUNTA ORIGINAL: {query}

INSTRUCOES:
1. Mantenha o mesmo significado e intencao
2. Use vocabulario e estruturas diferentes
3. Seja especifico e claro
4. Nao adicione informacoes extras
5. Retorne apenas as parafrases, uma por linha

PARAFRASES:"""

    response = await ainvoke_smart(prompt, temperature=0.8, max_output_tokens=200)
    variations = [line.strip() for line in response.strip().split('\n') if line.strip()]
    all_queries = [query] + variations[:num_variations - 1]
    return all_queries


def _reciprocal_rank_fusion(all_results: List[List[tuple[Document, float]]], k: int = 60, top_k: int = 5) -> List[tuple[Document, float, List[float]]]:
    """Combine multiple result lists using RRF"""
    rrf_scores = defaultdict(float)
    doc_map = {}
    original_scores = defaultdict(list)

    for result_list in all_results:
        for rank, (doc, score) in enumerate(result_list, start=1):
            content = doc.page_content
            rrf_scores[content] += 1.0 / (k + rank)
            doc_map[content] = doc
            original_scores[content].append(score)

    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    result = [(doc_map[content], rrf_score, original_scores[content]) for content, rrf_score in sorted_docs]
    return result
