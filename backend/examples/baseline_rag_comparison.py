"""
Comparação: Código Antigo vs Refatorado com PromptTemplate

Este arquivo mostra a diferença entre usar f-strings simples
e usar PromptTemplate do LangChain.
"""

import asyncio
import time
from typing import Dict, Any

from core.llm import get_llm
from core.embeddings import get_query_embedding_model
from core.vector_store import get_vector_store
from core.prompts import BASELINE_RAG_TEMPLATE  # ← Novo import
from config import settings


# ============================================
# VERSÃO ANTIGA (F-STRING)
# ============================================


def _build_prompt_old(query: str, context: str) -> str:
    """
    Versão antiga: Prompt hard-coded como f-string.

    Problemas:
    - ❌ Hard-coded no código
    - ❌ Difícil de reutilizar
    - ❌ Não valida variáveis
    - ❌ Difícil de testar isoladamente
    """
    return f"""Voce e um assistente especializado em responder perguntas baseado APENAS no contexto fornecido.

CONTEXTO:
{context}

PERGUNTA: {query}

INSTRUCOES:
1. Responda a pergunta usando APENAS as informacoes do contexto acima
2. Se a resposta nao estiver no contexto, diga: "Nao encontrei informacoes suficientes no contexto para responder essa pergunta."
3. Seja preciso e objetivo
4. Cite trechos relevantes quando apropriado

RESPOSTA:"""


async def baseline_rag_old(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Baseline RAG - Versão Antiga com F-String

    Usa função _build_prompt_old() com f-string simples.
    """
    start_time = time.time()

    # Initialize
    vector_store = get_vector_store()
    llm = get_llm()

    # Retrieve
    retrieved_docs = vector_store.similarity_search_with_score(query, k=top_k)

    # Build context
    context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs])

    # Build prompt (versão antiga) ← AQUI
    prompt = _build_prompt_old(query, context)

    # Generate
    response = llm.invoke(prompt)

    return {
        "query": query,
        "answer": response.content,
        "sources": [
            {"content": doc.page_content, "score": float(score)}
            for doc, score in retrieved_docs
        ],
        "latency_ms": round((time.time() - start_time) * 1000, 2),
        "method": "old_fstring",
    }


# ============================================
# VERSÃO NOVA (PROMPTTEMPLATE)
# ============================================


async def baseline_rag_new(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Baseline RAG - Versão Nova com PromptTemplate

    Usa BASELINE_RAG_TEMPLATE do core.prompts.

    Vantagens:
    - ✅ Prompt centralizado e reutilizável
    - ✅ Validação automática de variáveis
    - ✅ Fácil de testar isoladamente
    - ✅ Fácil de versionar e modificar
    """
    start_time = time.time()

    # Initialize
    vector_store = get_vector_store()
    llm = get_llm()

    # Retrieve
    retrieved_docs = vector_store.similarity_search_with_score(query, k=top_k)

    # Build context
    context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs])

    # Build prompt (versão nova) ← MUDANÇA AQUI
    prompt = BASELINE_RAG_TEMPLATE.format(context=context, query=query)

    # Generate
    response = llm.invoke(prompt)

    return {
        "query": query,
        "answer": response.content,
        "sources": [
            {"content": doc.page_content, "score": float(score)}
            for doc, score in retrieved_docs
        ],
        "latency_ms": round((time.time() - start_time) * 1000, 2),
        "method": "new_prompttemplate",
    }


# ============================================
# VERSÃO COM CHAIN PATTERN (MAIS MODERNA)
# ============================================


async def baseline_rag_chain(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Baseline RAG - Versão com LCEL (LangChain Expression Language)

    Usa chain pattern para composição de operações.
    Mais moderno e idiomático no LangChain.

    Vantagens:
    - ✅ Todas as vantagens do PromptTemplate
    - ✅ Composição declarativa de operações
    - ✅ Mais fácil adicionar logging/tracing
    - ✅ Suporte a streaming automático
    """
    start_time = time.time()

    # Initialize
    vector_store = get_vector_store()
    llm = get_llm()

    # Build chain: Template → LLM
    chain = BASELINE_RAG_TEMPLATE | llm

    # Retrieve
    retrieved_docs = vector_store.similarity_search_with_score(query, k=top_k)

    # Build context
    context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs])

    # Execute chain ← DIFERENÇA AQUI
    response = chain.invoke({"context": context, "query": query})

    return {
        "query": query,
        "answer": response.content,
        "sources": [
            {"content": doc.page_content, "score": float(score)}
            for doc, score in retrieved_docs
        ],
        "latency_ms": round((time.time() - start_time) * 1000, 2),
        "method": "chain_pattern",
    }


# ============================================
# COMPARAÇÃO E TESTES
# ============================================


async def compare_all_methods(query: str, top_k: int = 5):
    """
    Compara todas as 3 versões lado a lado.

    Args:
        query: Pergunta para testar
        top_k: Número de documentos a recuperar

    Returns:
        Resultados das 3 versões para comparação
    """
    print("=" * 80)
    print("COMPARAÇÃO: Antigas vs Nova Implementação")
    print("=" * 80)

    # Método 1: F-String (Antigo)
    print("\n1️⃣ MÉTODO ANTIGO (F-STRING)")
    print("-" * 80)
    result_old = await baseline_rag_old(query, top_k)
    print(f"Resposta: {result_old['answer'][:200]}...")
    print(f"Latência: {result_old['latency_ms']}ms")
    print(f"Fontes: {len(result_old['sources'])} documentos")

    # Método 2: PromptTemplate (Novo)
    print("\n2️⃣ MÉTODO NOVO (PROMPTTEMPLATE)")
    print("-" * 80)
    result_new = await baseline_rag_new(query, top_k)
    print(f"Resposta: {result_new['answer'][:200]}...")
    print(f"Latência: {result_new['latency_ms']}ms")
    print(f"Fontes: {len(result_new['sources'])} documentos")

    # Método 3: Chain Pattern (Mais Moderno)
    print("\n3️⃣ MÉTODO CHAIN PATTERN (LCEL)")
    print("-" * 80)
    result_chain = await baseline_rag_chain(query, top_k)
    print(f"Resposta: {result_chain['answer'][:200]}...")
    print(f"Latência: {result_chain['latency_ms']}ms")
    print(f"Fontes: {len(result_chain['sources'])} documentos")

    # Comparação
    print("\n" + "=" * 80)
    print("ANÁLISE COMPARATIVA")
    print("=" * 80)

    # Verificar se respostas são idênticas
    answers_identical = (
        result_old["answer"] == result_new["answer"] == result_chain["answer"]
    )

    print(f"\n✅ Respostas idênticas: {answers_identical}")

    if not answers_identical:
        print("⚠️ ATENÇÃO: As respostas diferem!")
        print(
            "   Isso pode acontecer devido a não-determinismo do LLM (temperature > 0)"
        )
        print("   Para comparação exata, use temperature=0.0")

    # Comparar performance
    print("\n📊 PERFORMANCE:")
    print(f"   F-String:        {result_old['latency_ms']}ms")
    print(f"   PromptTemplate:  {result_new['latency_ms']}ms")
    print(f"   Chain Pattern:   {result_chain['latency_ms']}ms")

    overhead = result_new["latency_ms"] - result_old["latency_ms"]
    print(f"\n   Overhead PromptTemplate: {overhead:.2f}ms")
    print(
        f"   (Overhead é negligível: {overhead/result_old['latency_ms']*100:.2f}% do tempo total)"
    )

    return {
        "old_fstring": result_old,
        "new_prompttemplate": result_new,
        "chain_pattern": result_chain,
        "answers_identical": answers_identical,
    }


# ============================================
# EXEMPLO DE USO
# ============================================


async def main():
    """Exemplo de comparação das 3 versões"""

    query = "O que é Python?"

    print("\n🔍 QUERY:", query)

    results = await compare_all_methods(query, top_k=3)

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)

    print("\n📝 RECOMENDAÇÃO:")
    print("   ✅ Use PromptTemplate (método 2) ou Chain Pattern (método 3)")
    print("   ✅ Evite F-Strings para prompts (método 1)")
    print("\n💡 VANTAGENS DO PROMPTTEMPLATE:")
    print("   • Validação automática de variáveis")
    print("   • Reutilização em múltiplos lugares")
    print("   • Fácil versionamento e testes")
    print("   • Overhead de performance negligível")
    print("   • Melhor organização do código")

    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Adicionar BASELINE_RAG_TEMPLATE em core/prompts.py")
    print("   2. Refatorar baseline_rag.py para usar o template")
    print("   3. Implementar HyDE, Reranking e Agentic com templates")
    print("   4. Adicionar testes para prompts")


if __name__ == "__main__":
    # Para executar:
    # python -m examples.baseline_rag_comparison
    asyncio.run(main())
