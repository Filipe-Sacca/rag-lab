"""
Adaptive RAG - Prompts Module (Simplified - 4 Essential Techniques)

Centralized prompts for query classification and routing decisions.
Focused on 4 core techniques that cover 95%+ of real-world use cases.

Techniques:
- baseline: Simple, factual queries (~60% of traffic)
- reranking: High precision needs (~15% of traffic)
- subquery: Complex multi-part queries (~15% of traffic)
- hyde: Abstract/conceptual queries (~10% of traffic)
"""

from langchain_core.prompts import PromptTemplate


# ============================================
# Query Classification Prompt (Simplified)
# ============================================
CLASSIFICATION_PROMPT = PromptTemplate.from_template("""Você é um classificador de perguntas para um sistema RAG.

Analise a pergunta e classifique em UMA das 4 categorias:

**CATEGORIAS:**

1. **simple** - Pergunta direta e factual
   - Indicadores: "O que é", "Qual", "Quando", "Onde", "Quem", "Defina"
   - Exemplo: "O que é Python?", "Qual a capital do Brasil?"
   - Esperado: Resposta curta e factual

2. **complex** - Pergunta com múltiplas partes ou comparação
   - Indicadores: "Compare", "diferença entre", "e também", "além de", "múltiplos", "vantagens e desvantagens"
   - Exemplo: "Compare Python e Java", "Quais são os prós e contras de X?"
   - Esperado: Resposta abrangente cobrindo vários aspectos

3. **abstract** - Pergunta conceitual ou explicativa
   - Indicadores: "Como funciona", "Por que", "Explique", "De que forma"
   - Exemplo: "Como funciona o machine learning?", "Por que usar microservices?"
   - Esperado: Explicação detalhada de conceitos

4. **precision** - Pergunta técnica que requer alta precisão
   - Indicadores: Termos técnicos específicos, jargão de domínio, linguagem formal
   - Domínios: Médico, legal, financeiro, científico, código
   - Exemplo: "Qual a dosagem de X para Y?", "Quais os requisitos legais para Z?"
   - Esperado: Resposta precisa e verificável

**PERGUNTA:**
{query}

**REGRAS:**
- Responda APENAS com uma palavra: simple, complex, abstract, ou precision
- Na dúvida entre simple e outra, escolha simple (mais rápido)
- Na dúvida entre complex e abstract, escolha complex (mais cobertura)

**CATEGORIA:**""")


# ============================================
# Category to Technique Mapping (Simplified)
# ============================================
CATEGORY_TO_TECHNIQUE = {
    "simple": "baseline",
    "complex": "subquery",
    "abstract": "hyde",
    "precision": "reranking",
}

# Default fallback technique
DEFAULT_TECHNIQUE = "baseline"

# Valid categories for validation
VALID_CATEGORIES = ["simple", "complex", "abstract", "precision"]


# ============================================
# Technique Descriptions
# ============================================
TECHNIQUE_DESCRIPTIONS = {
    "baseline": """
        Baseline RAG: Busca tradicional embed → search → generate.
        Rápido e eficiente para perguntas simples.
        Latência: ~1.2s | Custo: $0.002
    """,
    "reranking": """
        Reranking RAG: Re-ordena resultados com cross-encoder.
        Máxima precisão para queries técnicas.
        Latência: ~2.5s | Custo: $0.003
    """,
    "subquery": """
        Sub-Query RAG: Decompõe perguntas complexas em sub-perguntas.
        Cobertura completa para queries multi-parte.
        Latência: ~3.5s | Custo: $0.008
    """,
    "hyde": """
        HyDE RAG: Hypothetical Document Embeddings.
        Melhor para queries abstratas e conceituais.
        Latência: ~2.5s | Custo: $0.004
    """,
}


# ============================================
# Routing Reasons (for execution_details)
# ============================================
ROUTING_REASONS = {
    "simple": "Pergunta simples/direta → baseline (rápido e eficiente)",
    "complex": "Pergunta complexa/multi-parte → subquery (decomposição)",
    "abstract": "Pergunta abstrata/conceitual → hyde (embeddings hipotéticos)",
    "precision": "Alta precisão necessária → reranking (cross-encoder)",
}


def get_routing_reason(query_type: str) -> str:
    """Get human-readable routing explanation."""
    return ROUTING_REASONS.get(query_type, f"Classificação {query_type} → {CATEGORY_TO_TECHNIQUE.get(query_type, DEFAULT_TECHNIQUE)}")
