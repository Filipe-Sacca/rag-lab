"""
RAG Evaluation Module - High Granularity RAGAS Implementation

Implements RAGAS-style metrics with claim-level extraction and verification
for maximum evaluation granularity and accuracy.

Metrics:
- faithfulness: Claim-based verification (RAGAS original methodology)
- answer_relevancy: Reverse question generation + semantic comparison
- context_precision: Per-chunk relevance with Average Precision
- context_recall: Context utilization measurement
- hallucination_score: Inverse faithfulness for hallucination detection
- answer_completeness: Coverage of question aspects

Trade-off: Higher granularity = more API calls = higher latency/cost
Estimated: 4-8 API calls per evaluation vs 4 calls in simple mode
"""

from typing import Dict, List, Tuple
import logging
import re
import json

from config import settings

logger = logging.getLogger(__name__)


# Use Live API for unlimited requests - NO FALLBACK to Standard API
def _generate_with_live_api(prompt: str, temperature: float = 0.1, default: str = "{}") -> str:
    """
    Generate content using Live API (unlimited RPM/RPD).

    NO FALLBACK - Standard API causes 429 errors.
    If Live API fails, returns default value instead of causing quota issues.
    """
    try:
        from core.llm_live import live_invoke_sync

        # Use Live API ONLY
        response = live_invoke_sync(
            prompt=prompt,
            temperature=temperature,
            max_output_tokens=2000,
        )
        return response.strip() if response else default

    except Exception as e:
        # NO FALLBACK to Standard API - it causes 429 errors!
        logger.error(f"Live API failed for RAGAS: {e}")
        logger.warning("Returning default value instead of using Standard API (quota issues)")
        return default


def _safe_generate(model, prompt: str, default: str = "{}") -> str:
    """
    Safely generate content using Live API.

    Note: The 'model' parameter is kept for backward compatibility
    but is ignored - we always use Live API.
    """
    # Extract temperature from model config if available
    temperature = 0.1
    if hasattr(model, '_generation_config') and hasattr(model._generation_config, 'temperature'):
        temperature = model._generation_config.temperature

    return _generate_with_live_api(prompt, temperature, default)


def _get_model(temperature: float = 0.1):
    """Get a model-like object for backward compatibility."""
    class _ModelWrapper:
        def __init__(self, temp):
            self._temperature = temp
            self._generation_config = type('Config', (), {'temperature': temp})()

    return _ModelWrapper(temperature)


def _get_model_text(temperature: float = 0.1):
    """Get model instance for text (non-JSON) responses."""
    return _get_model(temperature)


def _parse_json(text: str, default: dict | list = None) -> dict | list:
    """Parse JSON from text, handling various formats."""
    if default is None:
        default = {}
    try:
        # Try direct JSON parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        # Try to find JSON object/array in text
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
        return default


def _parse_score(text: str, default: float = 0.0) -> float:
    """Parse a score from text, handling various formats."""
    try:
        # Try direct float conversion
        score = float(text)
        return max(0.0, min(1.0, score))
    except ValueError:
        # Try to extract a number
        numbers = re.findall(r'0?\.\d+|1\.0|0|1', text)
        if numbers:
            score = float(numbers[0])
            return max(0.0, min(1.0, score))
        return default


# =============================================================================
# FAITHFULNESS - Claim-Based Verification (RAGAS Original)
# =============================================================================

def _extract_claims(answer: str) -> List[str]:
    """
    Extract factual claims from the answer.

    RAGAS Step 1: Decompose answer into atomic factual statements.
    """
    model = _get_model(temperature=0.1)

    prompt = f"""Extraia TODAS as afirmações factuais atômicas desta resposta.
Cada claim deve ser uma única afirmação verificável.

RESPOSTA:
{answer}

Retorne um JSON com a lista de claims:
{{"claims": ["claim1", "claim2", "claim3", ...]}}

REGRAS:
- Cada claim deve ser uma afirmação factual única e atômica
- Não inclua opiniões ou julgamentos subjetivos
- Divida afirmações compostas em claims separados
- Mantenha o significado original
- Mínimo 1 claim, máximo 15 claims

Exemplo:
Resposta: "Python é uma linguagem de programação criada por Guido van Rossum em 1991. É conhecida por sua sintaxe limpa."
Claims: ["Python é uma linguagem de programação", "Python foi criada por Guido van Rossum", "Python foi criada em 1991", "Python é conhecida por sua sintaxe limpa"]
"""

    result = _safe_generate(model, prompt, '{"claims": []}')
    parsed = _parse_json(result, {"claims": []})
    claims = parsed.get("claims", [])

    # Fallback: se não extraiu claims, use a resposta inteira como um claim
    if not claims and answer:
        claims = [answer[:500]]

    logger.info(f"Extracted {len(claims)} claims from answer")
    return claims[:15]  # Limit to 15 claims


def _verify_claim(claim: str, context: str) -> Tuple[bool, str]:
    """
    Verify if a claim is supported by the context.

    RAGAS Step 2: Check each claim against context.

    Returns:
        Tuple of (is_supported: bool, reasoning: str)
    """
    model = _get_model(temperature=0.0)  # Deterministic for verification

    prompt = f"""Verifique se o claim é SUPORTADO pelo contexto fornecido.

CLAIM:
{claim}

CONTEXTO:
{context[:6000]}

Responda em JSON:
{{
    "verdict": "supported" | "not_supported" | "partial",
    "reasoning": "explicação breve de por que o claim é ou não suportado",
    "confidence": 0.0-1.0
}}

CRITÉRIOS:
- "supported": O contexto contém informação que confirma o claim
- "partial": O contexto suporta parcialmente ou implica o claim
- "not_supported": O contexto não contém informação para verificar o claim OU contradiz o claim

IMPORTANTE:
- Inferências lógicas razoáveis contam como "supported"
- Se o claim é conhecimento geral básico não contradito, marque "supported"
- Se o claim contradiz o contexto, marque "not_supported"
"""

    result = _safe_generate(model, prompt, '{"verdict": "not_supported", "confidence": 0.5}')
    parsed = _parse_json(result, {"verdict": "not_supported", "confidence": 0.5})

    verdict = parsed.get("verdict", "not_supported")
    reasoning = parsed.get("reasoning", "")

    is_supported = verdict in ["supported", "partial"]
    return is_supported, reasoning


def calculate_faithfulness_sync(
    answer: str,
    contexts: List[str],
) -> Dict[str, any]:
    """
    Calculate faithfulness score using claim extraction and verification.

    RAGAS Original Methodology:
    1. Extract atomic claims from the answer
    2. Verify each claim against the context
    3. Score = verified_claims / total_claims

    Returns:
        Dict with score and detailed claim analysis
    """
    if not answer or not contexts:
        return {"score": 0.0, "claims": [], "details": "Empty input"}

    try:
        combined_context = "\n---\n".join(contexts)

        # Step 1: Extract claims
        claims = _extract_claims(answer)

        if not claims:
            return {"score": 0.0, "claims": [], "details": "No claims extracted"}

        # Step 2: Verify each claim
        claim_results = []
        supported_count = 0

        for claim in claims:
            is_supported, reasoning = _verify_claim(claim, combined_context)
            claim_results.append({
                "claim": claim,
                "supported": is_supported,
                "reasoning": reasoning
            })
            if is_supported:
                supported_count += 1

        # Step 3: Calculate score
        score = supported_count / len(claims) if claims else 0.0

        logger.info(f"Faithfulness: {score:.3f} ({supported_count}/{len(claims)} claims supported)")

        return {
            "score": round(score, 4),
            "total_claims": len(claims),
            "supported_claims": supported_count,
            "claims": claim_results,
            "details": f"{supported_count}/{len(claims)} claims verified"
        }

    except Exception as e:
        logger.error(f"Faithfulness calculation failed: {e}")
        return {"score": 0.0, "claims": [], "details": str(e)}


# =============================================================================
# ANSWER RELEVANCY - Reverse Question Generation
# =============================================================================

def _generate_reverse_questions(answer: str, n: int = 3) -> List[str]:
    """
    Generate questions that the answer would address.

    RAGAS methodology: If answer is relevant, generated questions
    should be similar to the original question.
    """
    model = _get_model(temperature=0.3)  # Some creativity for diverse questions

    prompt = f"""Dado esta resposta, gere {n} perguntas diferentes que esta resposta poderia estar respondendo.

RESPOSTA:
{answer}

Retorne em JSON:
{{"questions": ["pergunta1", "pergunta2", "pergunta3"]}}

REGRAS:
- Gere perguntas que a resposta DIRETAMENTE responde
- Perguntas devem ser diversas mas relacionadas
- Use português natural
- Cada pergunta deve fazer sentido isoladamente
"""

    result = _safe_generate(model, prompt, '{"questions": []}')
    parsed = _parse_json(result, {"questions": []})

    questions = parsed.get("questions", [])
    logger.info(f"Generated {len(questions)} reverse questions")
    return questions[:n]


def _calculate_question_similarity(original: str, generated: str) -> float:
    """
    Calculate semantic similarity between original and generated question.
    """
    model = _get_model(temperature=0.0)

    prompt = f"""Avalie a similaridade semântica entre estas duas perguntas.

PERGUNTA ORIGINAL:
{original}

PERGUNTA GERADA:
{generated}

Retorne em JSON:
{{"similarity": 0.0-1.0, "reasoning": "explicação breve"}}

ESCALA:
- 1.0: Perguntas semanticamente idênticas (mesmo significado)
- 0.8: Perguntas muito similares (variações da mesma pergunta)
- 0.6: Perguntas relacionadas (mesmo tópico, foco diferente)
- 0.4: Perguntas vagamente relacionadas
- 0.2: Perguntas pouco relacionadas
- 0.0: Perguntas completamente diferentes
"""

    result = _safe_generate(model, prompt, '{"similarity": 0.5}')
    parsed = _parse_json(result, {"similarity": 0.5})

    return parsed.get("similarity", 0.5)


def calculate_answer_relevancy_sync(
    query: str,
    answer: str,
) -> Dict[str, any]:
    """
    Calculate answer relevancy using reverse question generation.

    RAGAS Original Methodology:
    1. Generate N questions that the answer would address
    2. Compare each generated question with the original
    3. Score = average semantic similarity

    Returns:
        Dict with score and detailed question analysis
    """
    if not query or not answer:
        return {"score": 0.0, "questions": [], "details": "Empty input"}

    try:
        # Step 1: Generate reverse questions
        generated_questions = _generate_reverse_questions(answer, n=3)

        if not generated_questions:
            # Fallback to simple evaluation
            model = _get_model_text(temperature=0.1)
            prompt = f"""Avalie de 0.0 a 1.0 se a resposta é relevante para a pergunta.

PERGUNTA: {query}
RESPOSTA: {answer}

Responda APENAS com um número (ex: 0.75):"""

            result = _safe_generate(model, prompt, "0.5")
            score = _parse_score(result, 0.5)
            return {"score": score, "questions": [], "details": "Fallback mode"}

        # Step 2: Calculate similarity for each generated question
        similarities = []
        question_results = []

        for gen_q in generated_questions:
            sim = _calculate_question_similarity(query, gen_q)
            similarities.append(sim)
            question_results.append({
                "generated_question": gen_q,
                "similarity": round(sim, 3)
            })

        # Step 3: Average similarity
        score = sum(similarities) / len(similarities) if similarities else 0.0

        logger.info(f"Answer relevancy: {score:.3f}")

        return {
            "score": round(score, 4),
            "questions": question_results,
            "avg_similarity": round(score, 4),
            "details": f"Based on {len(generated_questions)} reverse questions"
        }

    except Exception as e:
        logger.error(f"Answer relevancy calculation failed: {e}")
        return {"score": 0.0, "questions": [], "details": str(e)}


# =============================================================================
# CONTEXT PRECISION - Per-Chunk Average Precision
# =============================================================================

def _evaluate_chunk_relevance(query: str, chunk: str, chunk_index: int) -> Dict:
    """
    Evaluate if a single chunk is relevant to the query.

    Returns relevance score and reasoning for the chunk.
    """
    model = _get_model(temperature=0.0)

    prompt = f"""Avalie se este chunk de contexto é relevante para responder a pergunta.

PERGUNTA:
{query}

CHUNK #{chunk_index + 1}:
{chunk[:2000]}

Retorne em JSON:
{{
    "relevant": true | false,
    "relevance_score": 0.0-1.0,
    "reasoning": "explicação breve"
}}

CRITÉRIOS:
- relevant=true se o chunk contém informação útil para responder a pergunta
- relevance_score indica o grau de utilidade (1.0 = essencial, 0.5 = parcialmente útil, 0.0 = irrelevante)
"""

    result = _safe_generate(model, prompt, '{"relevant": false, "relevance_score": 0.0}')
    parsed = _parse_json(result, {"relevant": False, "relevance_score": 0.0})

    return {
        "chunk_index": chunk_index,
        "relevant": parsed.get("relevant", False),
        "relevance_score": parsed.get("relevance_score", 0.0),
        "reasoning": parsed.get("reasoning", "")
    }


def calculate_context_precision_sync(
    query: str,
    contexts: List[str],
    answer: str,
) -> Dict[str, any]:
    """
    Calculate context precision using per-chunk evaluation.

    Methodology:
    1. Evaluate each chunk for relevance
    2. Calculate precision = relevant_chunks / total_chunks
    3. Calculate Average Precision (AP) considering rank order

    Average Precision rewards having relevant chunks ranked higher.

    Returns:
        Dict with precision, AP, and per-chunk analysis
    """
    if not contexts:
        return {"score": 0.0, "chunks": [], "details": "No contexts"}

    try:
        # Evaluate each chunk
        chunk_results = []
        relevant_count = 0
        precision_at_k_sum = 0.0

        for i, chunk in enumerate(contexts):
            result = _evaluate_chunk_relevance(query, chunk, i)
            chunk_results.append(result)

            if result["relevant"]:
                relevant_count += 1
                # Precision@k for AP calculation
                precision_at_k = relevant_count / (i + 1)
                precision_at_k_sum += precision_at_k

        # Simple precision
        precision = relevant_count / len(contexts) if contexts else 0.0

        # Average Precision (AP) - rewards relevant chunks appearing earlier
        average_precision = precision_at_k_sum / relevant_count if relevant_count > 0 else 0.0

        # Combined score (weighted average of precision and AP)
        score = 0.5 * precision + 0.5 * average_precision

        logger.info(f"Context precision: {score:.3f} (P={precision:.3f}, AP={average_precision:.3f})")

        return {
            "score": round(score, 4),
            "precision": round(precision, 4),
            "average_precision": round(average_precision, 4),
            "relevant_chunks": relevant_count,
            "total_chunks": len(contexts),
            "chunks": chunk_results,
            "details": f"{relevant_count}/{len(contexts)} chunks relevant"
        }

    except Exception as e:
        logger.error(f"Context precision calculation failed: {e}")
        return {"score": 0.0, "chunks": [], "details": str(e)}


# =============================================================================
# CONTEXT RECALL / UTILIZATION
# =============================================================================

def calculate_context_utilization_sync(
    contexts: List[str],
    answer: str,
) -> Dict[str, any]:
    """
    Calculate how much of the context was utilized in the answer.

    Methodology:
    1. Identify key information pieces in the context
    2. Check which pieces appear in the answer
    3. Score = utilized_info / total_info

    Returns:
        Dict with score and utilization analysis
    """
    if not contexts or not answer:
        return {"score": 0.0, "details": "Empty input"}

    try:
        model = _get_model(temperature=0.1)
        combined_context = "\n---\n".join(contexts)[:8000]

        prompt = f"""Analise quanto do contexto foi utilizado na resposta.

CONTEXTOS FORNECIDOS ({len(contexts)} chunks):
{combined_context}

RESPOSTA GERADA:
{answer}

Retorne em JSON:
{{
    "utilization_score": 0.0-1.0,
    "key_facts_in_context": ["fato1", "fato2", ...],
    "facts_used_in_answer": ["fato1", "fato3", ...],
    "facts_not_used": ["fato2", ...],
    "reasoning": "explicação"
}}

CRITÉRIOS:
- 1.0: Todos os fatos relevantes do contexto foram utilizados
- 0.7: A maioria dos fatos importantes foi utilizada
- 0.5: Metade dos fatos relevantes foi utilizada
- 0.3: Poucos fatos do contexto foram utilizados
- 0.0: Nenhum fato do contexto foi utilizado
"""

        result = _safe_generate(model, prompt, '{"utilization_score": 0.5}')
        parsed = _parse_json(result, {"utilization_score": 0.5})

        score = parsed.get("utilization_score", 0.5)
        key_facts = parsed.get("key_facts_in_context", [])
        facts_used = parsed.get("facts_used_in_answer", [])

        logger.info(f"Context utilization: {score:.3f}")

        return {
            "score": round(score, 4),
            "key_facts_total": len(key_facts),
            "facts_utilized": len(facts_used),
            "key_facts": key_facts[:10],  # Limit for response size
            "facts_used": facts_used[:10],
            "reasoning": parsed.get("reasoning", ""),
            "details": f"Utilized {len(facts_used)}/{len(key_facts)} key facts"
        }

    except Exception as e:
        logger.error(f"Context utilization calculation failed: {e}")
        return {"score": 0.0, "details": str(e)}


# =============================================================================
# NEW METRICS: Hallucination & Completeness
# =============================================================================

def calculate_hallucination_score_sync(
    answer: str,
    contexts: List[str],
) -> Dict[str, any]:
    """
    Calculate hallucination score - inverse of faithfulness focused on detecting
    fabricated information.

    Returns:
        Dict with hallucination score (0 = no hallucination, 1 = full hallucination)
    """
    if not answer or not contexts:
        return {"score": 0.0, "hallucinations": [], "details": "Empty input"}

    try:
        model = _get_model(temperature=0.0)
        combined_context = "\n---\n".join(contexts)[:8000]

        prompt = f"""Identifique afirmações na resposta que são ALUCINAÇÕES (não suportadas pelo contexto).

CONTEXTO:
{combined_context}

RESPOSTA:
{answer}

Retorne em JSON:
{{
    "hallucination_score": 0.0-1.0,
    "hallucinations": [
        {{"statement": "afirmação alucinada", "reason": "por que é alucinação"}}
    ],
    "total_statements": N,
    "hallucinated_statements": N
}}

DEFINIÇÃO DE ALUCINAÇÃO:
- Informação que CONTRADIZ o contexto
- Fatos específicos que NÃO ESTÃO no contexto e não são conhecimento geral básico
- Números, datas, nomes inventados

NÃO É ALUCINAÇÃO:
- Conhecimento geral verdadeiro
- Inferências lógicas razoáveis
- Reformulação do contexto com outras palavras
"""

        result = _safe_generate(model, prompt, '{"hallucination_score": 0.0, "hallucinations": []}')
        parsed = _parse_json(result, {"hallucination_score": 0.0, "hallucinations": []})

        score = parsed.get("hallucination_score", 0.0)
        hallucinations = parsed.get("hallucinations", [])

        logger.info(f"Hallucination score: {score:.3f} ({len(hallucinations)} hallucinations found)")

        return {
            "score": round(score, 4),
            "hallucinations": hallucinations[:5],  # Limit
            "total_statements": parsed.get("total_statements", 0),
            "hallucinated_count": len(hallucinations),
            "details": f"{len(hallucinations)} potential hallucinations detected"
        }

    except Exception as e:
        logger.error(f"Hallucination detection failed: {e}")
        return {"score": 0.0, "hallucinations": [], "details": str(e)}


def calculate_answer_completeness_sync(
    query: str,
    answer: str,
) -> Dict[str, any]:
    """
    Calculate answer completeness - does the answer cover all aspects of the question?

    Returns:
        Dict with completeness score and aspect analysis
    """
    if not query or not answer:
        return {"score": 0.0, "aspects": [], "details": "Empty input"}

    try:
        model = _get_model(temperature=0.1)

        prompt = f"""Analise se a resposta cobre todos os aspectos da pergunta.

PERGUNTA:
{query}

RESPOSTA:
{answer}

Retorne em JSON:
{{
    "completeness_score": 0.0-1.0,
    "question_aspects": ["aspecto1", "aspecto2", ...],
    "aspects_covered": ["aspecto1", ...],
    "aspects_missing": ["aspecto2", ...],
    "reasoning": "explicação"
}}

CRITÉRIOS:
- 1.0: Todos os aspectos da pergunta foram abordados completamente
- 0.8: A maioria dos aspectos foi abordada
- 0.6: Aspectos principais cobertos, alguns secundários faltando
- 0.4: Apenas alguns aspectos cobertos
- 0.2: Resposta muito incompleta
- 0.0: Não aborda a pergunta
"""

        result = _safe_generate(model, prompt, '{"completeness_score": 0.5}')
        parsed = _parse_json(result, {"completeness_score": 0.5})

        score = parsed.get("completeness_score", 0.5)
        aspects = parsed.get("question_aspects", [])
        covered = parsed.get("aspects_covered", [])
        missing = parsed.get("aspects_missing", [])

        logger.info(f"Answer completeness: {score:.3f}")

        return {
            "score": round(score, 4),
            "total_aspects": len(aspects),
            "covered_aspects": len(covered),
            "aspects": aspects[:5],
            "covered": covered[:5],
            "missing": missing[:5],
            "reasoning": parsed.get("reasoning", ""),
            "details": f"Covered {len(covered)}/{len(aspects)} question aspects"
        }

    except Exception as e:
        logger.error(f"Completeness calculation failed: {e}")
        return {"score": 0.0, "aspects": [], "details": str(e)}


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================

def evaluate_rag_response_sync(
    query: str,
    answer: str,
    contexts: List[str],
    ground_truth: str | None = None,
    detailed: bool = True,
) -> Dict[str, any]:
    """
    Evaluate RAG response using high-granularity RAGAS metrics.

    This implementation uses claim-based verification, reverse question generation,
    and per-chunk analysis for maximum evaluation accuracy.

    Args:
        query: Original question
        answer: Generated answer
        contexts: List of retrieved chunks
        ground_truth: Expected answer (optional)
        detailed: Include detailed analysis in results

    Returns:
        Dict with scores and optionally detailed analysis

    Metrics returned:
        - faithfulness: Claim-based verification
        - answer_relevancy: Reverse question similarity
        - context_precision: Per-chunk + Average Precision
        - context_recall: Context utilization
        - hallucination_score: Fabrication detection
        - answer_completeness: Question aspect coverage
    """
    try:
        logger.info("Starting RAG evaluation (high granularity mode)...")

        # 1. Faithfulness (claim-based)
        faithfulness_result = calculate_faithfulness_sync(answer, contexts)

        # 2. Answer Relevancy (reverse questions)
        relevancy_result = calculate_answer_relevancy_sync(query, answer)

        # 3. Context Precision (per-chunk)
        precision_result = calculate_context_precision_sync(query, contexts, answer)

        # 4. Context Utilization (as recall proxy)
        utilization_result = calculate_context_utilization_sync(contexts, answer)

        # 5. Hallucination Score
        hallucination_result = calculate_hallucination_score_sync(answer, contexts)

        # 6. Answer Completeness
        completeness_result = calculate_answer_completeness_sync(query, answer)

        # Compile scores
        scores = {
            "faithfulness": faithfulness_result["score"],
            "answer_relevancy": relevancy_result["score"],
            "context_precision": precision_result["score"],
            "context_recall": utilization_result["score"],
            "hallucination_score": hallucination_result["score"],
            "answer_completeness": completeness_result["score"],
        }

        result = {"scores": scores}

        if detailed:
            result["detailed_analysis"] = {
                "faithfulness": faithfulness_result,
                "answer_relevancy": relevancy_result,
                "context_precision": precision_result,
                "context_recall": utilization_result,
                "hallucination": hallucination_result,
                "completeness": completeness_result,
            }

        logger.info(f"Evaluation complete: {scores}")
        return result

    except Exception as e:
        logger.error(f"RAG evaluation failed: {e}", exc_info=True)
        return {
            "scores": {
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "hallucination_score": 0.0,
                "answer_completeness": 0.0,
            },
            "error": str(e)
        }


# Async wrapper for FastAPI compatibility
async def evaluate_rag_response(
    query: str,
    answer: str,
    contexts: List[str],
    ground_truth: str | None = None,
    detailed: bool = False,
) -> Dict[str, float]:
    """
    Async wrapper for evaluate_rag_response_sync.

    Returns simplified scores dict for backward compatibility.
    For detailed analysis, use evaluate_rag_response_sync directly.
    """
    result = evaluate_rag_response_sync(query, answer, contexts, ground_truth, detailed=False)
    return result.get("scores", {
        "faithfulness": 0.0,
        "answer_relevancy": 0.0,
        "context_precision": 0.0,
        "context_recall": 0.0,
    })


# =============================================================================
# BATCH EVALUATION
# =============================================================================

def batch_evaluate_sync(
    queries: List[str],
    answers: List[str],
    contexts_list: List[List[str]],
    ground_truths: List[str] | None = None,
    detailed: bool = False,
) -> List[Dict]:
    """
    Evaluate multiple RAG responses in batch.
    """
    results = []
    logger.info(f"Running batch evaluation for {len(queries)} queries")

    for i, (query, answer, contexts) in enumerate(zip(queries, answers, contexts_list)):
        logger.info(f"Evaluating query {i+1}/{len(queries)}")
        result = evaluate_rag_response_sync(query, answer, contexts, detailed=detailed)
        results.append(result)

    logger.info(f"Batch evaluation complete: {len(results)} results")
    return results


async def batch_evaluate(
    queries: List[str],
    answers: List[str],
    contexts_list: List[List[str]],
    ground_truths: List[str] | None = None,
) -> List[Dict[str, float]]:
    """Async wrapper for batch_evaluate_sync."""
    results = batch_evaluate_sync(queries, answers, contexts_list, ground_truths, detailed=False)
    return [r.get("scores", {}) for r in results]


def get_average_scores(scores_list: List[Dict[str, float]]) -> Dict[str, float]:
    """Calculate average scores across multiple evaluations."""
    if not scores_list:
        return {}

    metric_names = set()
    for scores in scores_list:
        if isinstance(scores, dict):
            # Handle both {"scores": {...}} and flat dict formats
            actual_scores = scores.get("scores", scores)
            metric_names.update(k for k, v in actual_scores.items() if isinstance(v, (int, float)))

    averages = {}
    for metric in metric_names:
        values = []
        for scores in scores_list:
            actual_scores = scores.get("scores", scores) if isinstance(scores, dict) else {}
            if metric in actual_scores and isinstance(actual_scores[metric], (int, float)):
                values.append(actual_scores[metric])
        if values:
            averages[metric] = round(sum(values) / len(values), 4)

    return averages
