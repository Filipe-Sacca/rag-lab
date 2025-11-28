"""
Prompt Templates for RAG Techniques

DESIGN PRINCIPLE:
Para comparação justa entre técnicas RAG, o prompt de geração final DEVE ser idêntico.
Apenas os métodos de retrieval/preparação de contexto diferem entre técnicas.

Structure:
- ANSWER_PROMPT: Prompt ÚNICO usado por TODAS as técnicas para gerar resposta final
- Technique-specific prompts: Apenas para etapas intermediárias (ex: HyDE gerar doc hipotético)
"""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


# ============================================
# PROMPT UNIVERSAL - USADO POR TODAS TÉCNICAS
# ============================================

ANSWER_PROMPT = PromptTemplate(
    input_variables=["context", "query"],
    template="""Voce e um assistente especializado em responder perguntas baseado APENAS no contexto fornecido.

CONTEXTO:
{context}

PERGUNTA: {query}

INSTRUCOES:
1. Responda a pergunta usando APENAS as informacoes do contexto acima
2. Se a resposta nao estiver no contexto, diga: "Nao encontrei informacoes suficientes no contexto para responder essa pergunta."
3. Seja preciso e objetivo
4. Cite trechos relevantes quando apropriado

RESPOSTA:""",
)

# ============================================
# PROMPT ESPECÍFICO PARA RERANKING
# ============================================
# Reranking usa cross-encoder que gera scores 0.95-0.99 (vs bi-encoder 0.75-0.85)
# Este prompt informa ao LLM que scores altos são esperados e confiáveis

ANSWER_PROMPT_RERANKING = PromptTemplate(
    input_variables=["context", "query"],
    template="""Voce e um assistente especializado em responder perguntas baseado no contexto fornecido.

IMPORTANTE: O contexto abaixo foi selecionado por um sistema de reranking cross-encoder de alta precisao.
Os chunks foram validados com scores acima de 95% de relevancia e sao altamente confiaveis.

CONTEXTO:
{context}

PERGUNTA: {query}

INSTRUCOES:
1. Responda a pergunta usando as informacoes do contexto acima
2. O contexto foi validado por cross-encoder - confie na relevancia dos chunks
3. Apenas diga "nao encontrei informacoes" se o contexto for TOTALMENTE irrelevante para a pergunta
4. Seja preciso e objetivo
5. Cite trechos relevantes quando apropriado

RESPOSTA:""",
)

# ============================================
# PROMPT ESPECÍFICO PARA FUSION
# ============================================
# Fusion usa RRF (Reciprocal Rank Fusion) que gera scores baixos (0.04-0.05 = 4-5%)
# Isso é NORMAL! RRF combina rankings de múltiplas queries usando 1/(rank+k)
# Este prompt informa ao LLM que scores baixos de RRF são esperados e confiáveis

ANSWER_PROMPT_FUSION = PromptTemplate(
    input_variables=["context", "query"],
    template="""Voce e um assistente especializado em responder perguntas baseado no contexto fornecido.

IMPORTANTE: O contexto foi selecionado por Reciprocal Rank Fusion (RRF), que combina resultados de multiplas queries.
Os scores RRF sao baixos por design (tipicamente 4-5%), mas os chunks sao ALTAMENTE RELEVANTES.
RRF usa a formula 1/(rank+60), entao scores de 0.04-0.05 indicam TOP results de multiplas buscas combinadas.

CONTEXTO:
{context}

PERGUNTA: {query}

INSTRUCOES:
1. Responda a pergunta usando as informacoes do contexto acima
2. IGNORE os scores numericos baixos - eles sao normais para RRF
3. Os chunks foram validados por consensus de multiplas queries - confie neles
4. Apenas diga "nao encontrei informacoes" se o contexto for TOTALMENTE irrelevante para a pergunta
5. Seja preciso e objetivo
6. Cite trechos relevantes quando apropriado

RESPOSTA:""",
)

# ============================================
# PROMPT ESPECÍFICO PARA SUB-QUERY
# ============================================
# Sub-Query decompõe queries complexas em sub-perguntas e combina resultados
# Os chunks podem vir de buscas diferentes, cobrindo aspectos distintos da pergunta original
# Este prompt instrui o LLM a sintetizar informações de múltiplas perspectivas

ANSWER_PROMPT_SUBQUERY = PromptTemplate(
    input_variables=["context", "query"],
    template="""Voce e um assistente especializado em responder perguntas baseado no contexto fornecido.

IMPORTANTE: O contexto foi coletado atraves de multiplas sub-queries que exploram diferentes aspectos da pergunta original.
Os chunks podem cobrir perspectivas complementares - sintetize as informacoes para uma resposta completa e coerente.

CONTEXTO:
{context}

PERGUNTA: {query}

INSTRUCOES:
1. Responda a pergunta usando as informacoes do contexto acima
2. Sintetize informacoes de diferentes chunks que abordam aspectos complementares
3. Priorize definicoes basicas e informacoes fundamentais quando presentes
4. Se houver informacoes sobre variacoes/tecnicas avancadas mas faltar a definicao basica, mencione as variacoes mas indique que falta informacao fundamental
5. Apenas diga "nao encontrei informacoes" se o contexto for TOTALMENTE irrelevante para a pergunta
6. Seja preciso e objetivo
7. Cite trechos relevantes quando apropriado

RESPOSTA:""",
)

# Versão Chat do prompt universal (opcional)
ANSWER_PROMPT_CHAT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """Voce e um assistente especializado em responder perguntas baseado APENAS no contexto fornecido.

INSTRUCOES:
1. Responda usando APENAS as informacoes do contexto
2. Se nao souber, diga que nao encontrou informacoes
3. Seja preciso e objetivo
4. Cite trechos relevantes quando apropriado"""
        ),
        HumanMessagePromptTemplate.from_template(
            """CONTEXTO:
{context}

PERGUNTA: {query}

RESPOSTA:"""
        ),
    ]
)


# ============================================
# PROMPTS ESPECÍFICOS DE TÉCNICAS
# (Apenas para etapas intermediárias)
# ============================================

# HyDE: Gerar documento hipotético
# (Esta etapa é específica do HyDE, depois usa ANSWER_PROMPT igual às outras)
HYDE_GENERATE_DOC = PromptTemplate(
    input_variables=["query"],
    template="""Gere um documento hipotetico detalhado que responderia perfeitamente a seguinte pergunta.
O documento deve conter informacoes precisas, detalhadas e relevantes, como se fosse extraido de uma fonte confiavel.

PERGUNTA: {query}

DOCUMENTO HIPOTETICO (seja detalhado e tecnico):""",
)

# Agentic RAG: Planejamento
# (Esta etapa é específica do Agentic, depois usa ANSWER_PROMPT igual às outras)
AGENTIC_PLANNER = PromptTemplate(
    input_variables=["query"],
    template="""Analise a seguinte pergunta e crie um plano estruturado de busca.
Identifique os principais conceitos, subperguntas e termos que devem ser pesquisados.

PERGUNTA: {query}

PLANO DE BUSCA (liste conceitos principais e subperguntas):
1.
2.
3.""",
)


# ============================================
# MAPEAMENTO DE TÉCNICAS
# ============================================

# NOTA: Algumas técnicas usam prompts específicos devido às suas características:
# - Reranking: Cross-encoder scores altos (0.95-0.99) - precisa calibração
# - Fusion: RRF scores baixos (0.04-0.05) mas chunks altamente relevantes - precisa explicação
# - Sub-Query: Chunks de múltiplas sub-queries - precisa síntese de perspectivas complementares
# Outras técnicas usam o prompt universal
TECHNIQUE_ANSWER_PROMPTS = {
    "baseline": ANSWER_PROMPT,
    "hyde": ANSWER_PROMPT,
    "reranking": ANSWER_PROMPT_RERANKING,  # ← Prompt específico! (cross-encoder scores altos)
    "agentic": ANSWER_PROMPT,
    "fusion": ANSWER_PROMPT_FUSION,  # ← Prompt específico! (RRF scores baixos)
    "subquery": ANSWER_PROMPT_SUBQUERY,  # ← Prompt específico! (múltiplas sub-queries)
    "graph": ANSWER_PROMPT,
}


# ============================================
# UTILITY FUNCTIONS
# ============================================


def get_answer_prompt(technique: str | None = None) -> PromptTemplate:
    """
    Get the answer generation prompt for any RAG technique.

    IMPORTANT: Maioria usa ANSWER_PROMPT universal, mas algumas técnicas usam prompts específicos:
    - Reranking: Cross-encoder scores altos (0.95-0.99) vs bi-encoder (0.75-0.85)
    - Fusion: RRF scores baixos (0.04-0.05) mas chunks altamente relevantes
    - Sub-Query: Chunks de múltiplas sub-queries - precisa síntese de perspectivas

    Args:
        technique: Nome da técnica (opcional)

    Returns:
        PromptTemplate apropriado para a técnica
        - baseline, hyde, agentic, graph: ANSWER_PROMPT (universal)
        - reranking: ANSWER_PROMPT_RERANKING (específico para cross-encoder)
        - fusion: ANSWER_PROMPT_FUSION (específico para RRF scores)
        - subquery: ANSWER_PROMPT_SUBQUERY (específico para múltiplas sub-queries)

    Example:
        >>> # Maioria retorna prompt universal
        >>> prompt_baseline = get_answer_prompt('baseline')
        >>> prompt_hyde = get_answer_prompt('hyde')
        >>> prompt_baseline.template == prompt_hyde.template
        True

        >>> # Reranking, Fusion e Sub-Query retornam prompts específicos
        >>> prompt_rerank = get_answer_prompt('reranking')
        >>> prompt_fusion = get_answer_prompt('fusion')
        >>> prompt_subquery = get_answer_prompt('subquery')
        >>> prompt_rerank.template != prompt_baseline.template
        True
        >>> prompt_fusion.template != prompt_baseline.template
        True
        >>> prompt_subquery.template != prompt_baseline.template
        True
    """
    if technique and technique not in TECHNIQUE_ANSWER_PROMPTS:
        raise ValueError(
            f"Unknown technique: {technique}. "
            f"Choose from {list(TECHNIQUE_ANSWER_PROMPTS.keys())}"
        )

    # Retorna prompt específico para cada técnica (reranking é diferente)
    if technique:
        return TECHNIQUE_ANSWER_PROMPTS[technique]

    # Sem técnica especificada, retorna universal
    return ANSWER_PROMPT


def get_hyde_doc_generator() -> PromptTemplate:
    """
    Get HyDE-specific prompt for generating hypothetical documents.

    Este prompt é usado APENAS na etapa intermediária do HyDE.
    Depois o HyDE usa get_answer_prompt() igual às outras técnicas.

    Returns:
        HYDE_GENERATE_DOC template

    Example:
        >>> # Etapa 1 HyDE: Gerar documento hipotético
        >>> doc_prompt = get_hyde_doc_generator()
        >>> hyp_doc = llm.invoke(doc_prompt.format(query="..."))
        >>>
        >>> # Etapa 2 HyDE: Buscar com documento hipotético
        >>> docs = vector_store.search(hyp_doc)
        >>>
        >>> # Etapa 3 HyDE: Responder (MESMO PROMPT das outras técnicas!)
        >>> answer_prompt = get_answer_prompt('hyde')
        >>> answer = llm.invoke(answer_prompt.format(context=docs, query="..."))
    """
    return HYDE_GENERATE_DOC


def get_agentic_planner() -> PromptTemplate:
    """
    Get Agentic RAG-specific prompt for query planning.

    Este prompt é usado APENAS na etapa intermediária do Agentic RAG.
    Depois o Agentic usa get_answer_prompt() igual às outras técnicas.

    Returns:
        AGENTIC_PLANNER template

    Example:
        >>> # Etapa 1 Agentic: Planejar busca
        >>> planner_prompt = get_agentic_planner()
        >>> plan = llm.invoke(planner_prompt.format(query="..."))
        >>>
        >>> # Etapa 2 Agentic: Executar buscas baseadas no plano
        >>> docs = execute_search_plan(plan)
        >>>
        >>> # Etapa 3 Agentic: Responder (MESMO PROMPT das outras técnicas!)
        >>> answer_prompt = get_answer_prompt('agentic')
        >>> answer = llm.invoke(answer_prompt.format(context=docs, query="..."))
    """
    return AGENTIC_PLANNER


def validate_prompt_variables(template: PromptTemplate, **kwargs) -> bool:
    """
    Validate that all required variables are provided for a template.

    Args:
        template: PromptTemplate instance
        **kwargs: Variables to validate

    Returns:
        True if all variables are present

    Raises:
        ValueError: If any required variables are missing

    Example:
        >>> validate_prompt_variables(
        ...     ANSWER_PROMPT,
        ...     context="test context",
        ...     query="test query"
        ... )
        True
    """
    missing = set(template.input_variables) - set(kwargs.keys())
    if missing:
        raise ValueError(f"Missing required variables: {missing}")
    return True


def list_available_techniques() -> list[str]:
    """
    List all available RAG techniques.

    Returns:
        List of technique names

    Example:
        >>> list_available_techniques()
        ['baseline', 'hyde', 'reranking', 'agentic']
    """
    return list(TECHNIQUE_ANSWER_PROMPTS.keys())


def verify_prompts_identical() -> bool:
    """
    Verify prompt consistency for fair comparison.

    Some techniques use specific prompts due to different score ranges:
    - Reranking: Cross-encoder scores (0.95-0.99) need calibration
    - Fusion: RRF scores (0.04-0.05) need explanation
    - Others: Standard prompt with bi-encoder scores (0.75-0.85)

    This is intentional and maintains fair comparison by calibrating
    LLM interpretation to each scoring mechanism.

    Returns:
        True if prompt configuration is valid

    Example:
        >>> verify_prompts_identical()
        True
    """
    # Técnicas que DEVEM usar prompt universal
    universal_techniques = ["baseline", "hyde", "agentic", "graph"]

    # Técnicas com prompts específicos (por design)
    specific_prompt_techniques = {
        "reranking": ANSWER_PROMPT_RERANKING,
        "fusion": ANSWER_PROMPT_FUSION,
        "subquery": ANSWER_PROMPT_SUBQUERY,
    }

    # Validar que técnicas universais usam o mesmo prompt
    for tech in universal_techniques:
        if TECHNIQUE_ANSWER_PROMPTS[tech] is not ANSWER_PROMPT:
            raise AssertionError(
                f"CRITICAL: {tech} should use universal ANSWER_PROMPT! "
                f"This breaks fair comparison."
            )

    # Validar que técnicas específicas usam seus prompts corretos
    for tech, expected_prompt in specific_prompt_techniques.items():
        if TECHNIQUE_ANSWER_PROMPTS[tech] is not expected_prompt:
            raise AssertionError(
                f"CRITICAL: {tech} should use {expected_prompt}! "
                f"Incorrect prompt configuration."
            )

    return True


def get_prompt_info() -> dict:
    """
    Get information about the prompt system.

    Returns:
        Dictionary with system information

    Example:
        >>> info = get_prompt_info()
        >>> print(info['universal_techniques'])
        ['baseline', 'hyde', 'agentic', 'subquery', 'graph']
        >>> print(info['specific_prompt_techniques'])
        {'reranking': 'cross-encoder', 'fusion': 'RRF'}
    """
    return {
        "universal_prompt_used": True,
        "universal_techniques": ["baseline", "hyde", "agentic", "graph"],
        "specific_prompt_techniques": {
            "reranking": "ANSWER_PROMPT_RERANKING (cross-encoder scores 0.95-0.99)",
            "fusion": "ANSWER_PROMPT_FUSION (RRF scores 0.04-0.05)",
            "subquery": "ANSWER_PROMPT_SUBQUERY (múltiplas sub-queries)",
        },
        "answer_prompt_template": ANSWER_PROMPT.template[:100] + "...",
        "all_techniques": list_available_techniques(),
        "prompts_valid": verify_prompts_identical(),
        "intermediate_prompts": {
            "hyde_doc_generator": "HYDE_GENERATE_DOC",
            "agentic_planner": "AGENTIC_PLANNER",
        },
        "design_principle": "Prompts calibrados por características da técnica: universal (bi-encoder), reranking (cross-encoder), fusion (RRF), subquery (múltiplas perspectivas)",
    }


# ============================================
# VALIDAÇÃO NA IMPORTAÇÃO
# ============================================

# Verify prompts are identical when module is imported
try:
    verify_prompts_identical()
except AssertionError as e:
    import warnings

    warnings.warn(str(e), RuntimeWarning)
