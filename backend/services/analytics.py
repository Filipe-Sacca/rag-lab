"""
Analytics Service for RAG Lab

Aggregates execution data by technique and generates comparative analysis.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import RAGExecution
from core.llm import get_llm


def get_aggregated_stats(db: Session) -> Dict[str, Any]:
    """
    Aggregate all execution data by technique.

    Returns:
        Dict with aggregated stats per technique
    """
    # Query all executions grouped by technique
    # Join with RAGMetric to get metrics data
    from db.models import RAGMetric

    results = db.query(
        RAGExecution.technique_name,
        func.count(RAGExecution.id).label('total_executions'),
        func.avg(RAGMetric.latency_ms).label('avg_latency_ms'),
        func.min(RAGMetric.latency_ms).label('min_latency_ms'),
        func.max(RAGMetric.latency_ms).label('max_latency_ms'),
        func.avg(RAGMetric.faithfulness).label('avg_faithfulness'),
        func.avg(RAGMetric.answer_relevancy).label('avg_answer_relevancy'),
        func.avg(RAGMetric.context_precision).label('avg_context_precision'),
        func.avg(RAGMetric.context_recall).label('avg_context_recall'),
        func.avg(RAGMetric.chunks_retrieved).label('avg_chunks'),
        func.sum(RAGMetric.chunks_retrieved).label('total_chunks'),
    ).join(RAGMetric, RAGExecution.id == RAGMetric.execution_id, isouter=True
    ).group_by(RAGExecution.technique_name).all()

    # Get top 3 chunk scores per technique
    top_scores_by_technique = _get_top_chunk_scores(db)

    techniques_data = {}
    total_executions = 0

    for row in results:
        technique = row.technique_name or 'unknown'
        exec_count = row.total_executions or 0
        total_executions += exec_count

        # Get top scores for this technique
        top_scores = top_scores_by_technique.get(technique, {})

        techniques_data[technique] = {
            'technique': technique,
            'total_executions': exec_count,
            'metrics': {
                'latency': {
                    'avg_ms': round(row.avg_latency_ms or 0, 2),
                    'min_ms': round(row.min_latency_ms or 0, 2),
                    'max_ms': round(row.max_latency_ms or 0, 2),
                },
                'quality': {
                    'faithfulness': round(row.avg_faithfulness or 0, 4),
                    'answer_relevancy': round(row.avg_answer_relevancy or 0, 4),
                    'context_precision': round(row.avg_context_precision or 0, 4),
                    'context_recall': round(row.avg_context_recall or 0, 4),
                },
                'retrieval': {
                    'avg_chunks': round(row.avg_chunks or 0, 2),
                    'total_chunks': row.total_chunks or 0,
                    'top_scores': top_scores,
                }
            }
        }

    return {
        'total_executions': total_executions,
        'techniques_count': len(techniques_data),
        'techniques': techniques_data
    }


def _get_top_chunk_scores(db: Session) -> Dict[str, Dict[str, float]]:
    """
    Extract average top 3 chunk scores per technique from sources JSON.

    Returns:
        Dict mapping technique -> {avg_top1, avg_top2, avg_top3, avg_top3_mean}
    """
    # Get all executions with sources
    executions = db.query(
        RAGExecution.technique_name,
        RAGExecution.sources
    ).filter(RAGExecution.sources.isnot(None)).all()

    # Collect scores per technique
    scores_by_technique: Dict[str, List[List[float]]] = {}

    for technique, sources in executions:
        if not technique or not sources:
            continue

        # Extract scores from sources (supports multiple key formats)
        # - 'score': baseline, graph, hyde, subquery
        # - 'rerank_score': reranking technique (preferred)
        # - 'original_score': reranking fallback
        chunk_scores = []
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict):
                    score = source.get('rerank_score') or source.get('score') or source.get('original_score')
                    if score is not None:
                        chunk_scores.append(float(score))

        # Sort descending and take top 3
        chunk_scores.sort(reverse=True)
        top3 = chunk_scores[:3]

        if top3:
            if technique not in scores_by_technique:
                scores_by_technique[technique] = []
            scores_by_technique[technique].append(top3)

    # Calculate averages per technique
    result = {}
    for technique, all_top3 in scores_by_technique.items():
        if not all_top3:
            continue

        # Average for each position (top1, top2, top3)
        avg_top1 = sum(t[0] for t in all_top3) / len(all_top3) if all_top3 else 0
        avg_top2 = sum(t[1] for t in all_top3 if len(t) > 1) / len([t for t in all_top3 if len(t) > 1]) if any(len(t) > 1 for t in all_top3) else 0
        avg_top3 = sum(t[2] for t in all_top3 if len(t) > 2) / len([t for t in all_top3 if len(t) > 2]) if any(len(t) > 2 for t in all_top3) else 0

        # Average of top 3 scores
        all_scores = [s for top3 in all_top3 for s in top3]
        avg_top3_mean = sum(all_scores) / len(all_scores) if all_scores else 0

        result[technique] = {
            'avg_top1': round(avg_top1, 4),
            'avg_top2': round(avg_top2, 4),
            'avg_top3': round(avg_top3, 4),
            'avg_top3_mean': round(avg_top3_mean, 4),
        }

    return result


def get_rankings(aggregated_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate rankings for each metric.

    Returns:
        Dict with metric -> ranked list of techniques
    """
    techniques = aggregated_data.get('techniques', {})
    if not techniques:
        return {}

    rankings = {}

    # Latency (lower is better)
    rankings['fastest'] = sorted(
        techniques.keys(),
        key=lambda t: techniques[t]['metrics']['latency']['avg_ms']
    )

    # Faithfulness (higher is better)
    rankings['most_faithful'] = sorted(
        techniques.keys(),
        key=lambda t: techniques[t]['metrics']['quality']['faithfulness'],
        reverse=True
    )

    # Answer Relevancy (higher is better)
    rankings['most_relevant'] = sorted(
        techniques.keys(),
        key=lambda t: techniques[t]['metrics']['quality']['answer_relevancy'],
        reverse=True
    )

    # Context Precision (higher is better)
    rankings['best_precision'] = sorted(
        techniques.keys(),
        key=lambda t: techniques[t]['metrics']['quality']['context_precision'],
        reverse=True
    )

    # Context Recall (higher is better)
    rankings['best_recall'] = sorted(
        techniques.keys(),
        key=lambda t: techniques[t]['metrics']['quality']['context_recall'],
        reverse=True
    )

    # Best Top Chunk Scores (higher is better)
    techniques_with_scores = [
        t for t in techniques.keys()
        if techniques[t]['metrics']['retrieval'].get('top_scores', {}).get('avg_top3_mean', 0) > 0
    ]
    if techniques_with_scores:
        rankings['best_chunk_scores'] = sorted(
            techniques_with_scores,
            key=lambda t: techniques[t]['metrics']['retrieval']['top_scores']['avg_top3_mean'],
            reverse=True
        )

    return rankings


async def generate_llm_analysis(aggregated_data: Dict[str, Any], rankings: Dict[str, List[str]]) -> str:
    """
    Use Gemini to generate a comprehensive analysis of the techniques.

    Returns:
        String with the LLM-generated analysis
    """
    import asyncio

    techniques = aggregated_data.get('techniques', {})
    if not techniques:
        return "No data available for analysis. Execute some queries first."

    # Build context for the LLM
    context_parts = []
    context_parts.append(f"Total executions analyzed: {aggregated_data['total_executions']}")
    context_parts.append(f"Techniques compared: {', '.join(techniques.keys())}")
    context_parts.append("")

    for name, data in techniques.items():
        metrics = data['metrics']
        context_parts.append(f"## {name.upper()} ({data['total_executions']} executions)")
        context_parts.append(f"- Avg Latency: {metrics['latency']['avg_ms']}ms (min: {metrics['latency']['min_ms']}ms, max: {metrics['latency']['max_ms']}ms)")
        context_parts.append(f"- Faithfulness: {metrics['quality']['faithfulness']*100:.1f}%")
        context_parts.append(f"- Answer Relevancy: {metrics['quality']['answer_relevancy']*100:.1f}%")
        context_parts.append(f"- Context Precision: {metrics['quality']['context_precision']*100:.1f}%")
        context_parts.append(f"- Context Recall: {metrics['quality']['context_recall']*100:.1f}%")
        context_parts.append(f"- Avg Chunks Retrieved: {metrics['retrieval']['avg_chunks']}")
        # Add top chunk scores if available
        top_scores = metrics['retrieval'].get('top_scores', {})
        if top_scores:
            context_parts.append(f"- Top Chunk Scores: #1={top_scores.get('avg_top1', 0):.3f}, #2={top_scores.get('avg_top2', 0):.3f}, #3={top_scores.get('avg_top3', 0):.3f} (avg={top_scores.get('avg_top3_mean', 0):.3f})")
        context_parts.append("")

    context_parts.append("## RANKINGS")
    context_parts.append(f"- Fastest: {' > '.join(rankings.get('fastest', []))}")
    context_parts.append(f"- Most Faithful: {' > '.join(rankings.get('most_faithful', []))}")
    context_parts.append(f"- Most Relevant: {' > '.join(rankings.get('most_relevant', []))}")
    context_parts.append(f"- Best Precision: {' > '.join(rankings.get('best_precision', []))}")
    context_parts.append(f"- Best Recall: {' > '.join(rankings.get('best_recall', []))}")
    if rankings.get('best_chunk_scores'):
        context_parts.append(f"- Best Chunk Scores: {' > '.join(rankings.get('best_chunk_scores', []))}")

    context = "\n".join(context_parts)

    prompt = f"""You are an expert RAG (Retrieval-Augmented Generation) analyst.
Analyze the following comparative data from multiple RAG techniques and provide insights.

DATA:
{context}

Please provide a comprehensive analysis in Portuguese (Brazilian) including:

1. **Resumo Executivo** (2-3 frases)
2. **Melhor Técnica Geral** - Considerando trade-offs entre qualidade e performance
3. **Análise por Caso de Uso**:
   - Para queries simples e rápidas
   - Para queries que exigem alta precisão
   - Para melhor custo-benefício
4. **Pontos de Atenção** - Problemas ou anomalias identificadas
5. **Recomendações** - Sugestões práticas de melhoria

Keep the analysis concise but insightful. Use bullet points and clear formatting.
"""

    try:
        llm = get_llm(temperature=0.3, max_output_tokens=1500)
        # Run sync LLM call in thread pool to avoid blocking event loop
        response = await asyncio.to_thread(llm.invoke, prompt)
        return response.content
    except Exception as e:
        # Return fallback analysis on LLM failure
        import traceback
        print(f"LLM analysis failed: {e}")
        traceback.print_exc()
        return _generate_fallback_analysis(aggregated_data, rankings)


def _generate_fallback_analysis(aggregated_data: Dict[str, Any], rankings: Dict[str, List[str]]) -> str:
    """Generate a basic analysis without LLM when Gemini fails."""
    techniques = aggregated_data.get('techniques', {})
    total = aggregated_data.get('total_executions', 0)

    lines = [
        "## Análise Automática (sem LLM)",
        "",
        f"**Total de execuções analisadas:** {total}",
        f"**Técnicas comparadas:** {len(techniques)}",
        "",
        "### Rankings:",
    ]

    if rankings.get('fastest'):
        lines.append(f"- 🚀 **Mais Rápida:** {rankings['fastest'][0]}")
    if rankings.get('most_faithful'):
        lines.append(f"- ✅ **Mais Fiel:** {rankings['most_faithful'][0]}")
    if rankings.get('most_relevant'):
        lines.append(f"- 🎯 **Mais Relevante:** {rankings['most_relevant'][0]}")

    lines.append("")
    lines.append("*Nota: Análise simplificada. O serviço de IA está temporariamente indisponível.*")

    return "\n".join(lines)


async def get_full_analysis(db: Session) -> Dict[str, Any]:
    """
    Get complete analysis with aggregated data, rankings, and LLM insights.

    Returns:
        Complete analysis dict
    """
    # Get aggregated stats
    aggregated = get_aggregated_stats(db)

    # Get rankings
    rankings = get_rankings(aggregated)

    # Generate LLM analysis
    llm_analysis = await generate_llm_analysis(aggregated, rankings)

    return {
        'aggregated_data': aggregated,
        'rankings': rankings,
        'llm_analysis': llm_analysis,
    }
