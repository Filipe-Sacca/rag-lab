# 🎯 Guia: Refatorando para PromptTemplate do LangChain

## 📋 Índice
1. [O que é PromptTemplate?](#o-que-é-prompttemplate)
2. [Código Atual vs Refatorado](#código-atual-vs-refatorado)
3. [Implementação Passo a Passo](#implementação-passo-a-passo)
4. [Organização de Prompts](#organização-de-prompts)
5. [Vantagens e Desvantagens](#vantagens-e-desvantagens)
6. [Aplicando em Outras Técnicas](#aplicando-em-outras-técnicas)

---

## O que é PromptTemplate?

**PromptTemplate** é uma classe do LangChain que permite:
- ✅ **Reutilizar** prompts em diferentes lugares
- ✅ **Validar** variáveis automaticamente
- ✅ **Organizar** prompts em arquivos separados
- ✅ **Versionar** prompts facilmente
- ✅ **Testar** prompts de forma isolada
- ✅ **Compor** prompts complexos a partir de templates simples

---

## Código Atual vs Refatorado

### ❌ Código Atual (String Simples)

```python
# techniques/baseline_rag.py - Linha 206
def _build_prompt(query: str, context: str) -> str:
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

# Uso:
prompt = _build_prompt(query, context)
response = llm.invoke(prompt)
```

**Problemas**:
- 🔴 Hard-coded no código
- 🔴 Difícil de reutilizar em outras técnicas
- 🔴 Não valida variáveis
- 🔴 Não permite versionamento fácil
- 🔴 Difícil de testar isoladamente

---

### ✅ Código Refatorado (PromptTemplate)

```python
from langchain_core.prompts import PromptTemplate

# Opção 1: Template inline
RAG_PROMPT_TEMPLATE = PromptTemplate(
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

RESPOSTA:"""
)

# Uso:
prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)
response = llm.invoke(prompt)

# OU usar diretamente com chain:
chain = RAG_PROMPT_TEMPLATE | llm
response = chain.invoke({"context": context, "query": query})
```

**Vantagens**:
- ✅ Validação automática de variáveis
- ✅ Reutilizável em qualquer lugar
- ✅ Fácil de testar
- ✅ Pode usar partial() para preencher algumas variáveis
- ✅ Suporta composição de templates

---

## Implementação Passo a Passo

### Passo 1: Criar Arquivo de Prompts Centralizados

Crie: `backend/core/prompts.py`

```python
"""
Prompt Templates for RAG Techniques

Centralized prompt management using LangChain PromptTemplate.
"""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


# ============================================
# BASELINE RAG PROMPTS
# ============================================

BASELINE_RAG_SYSTEM = """Voce e um assistente especializado em responder perguntas baseado APENAS no contexto fornecido.

INSTRUCOES:
1. Responda a pergunta usando APENAS as informacoes do contexto acima
2. Se a resposta nao estiver no contexto, diga: "Nao encontrei informacoes suficientes no contexto para responder essa pergunta."
3. Seja preciso e objetivo
4. Cite trechos relevantes quando apropriado"""

BASELINE_RAG_TEMPLATE = PromptTemplate(
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

RESPOSTA:"""
)

# Versão Chat (mais moderno, suporta system/user/assistant roles)
BASELINE_RAG_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(BASELINE_RAG_SYSTEM),
    HumanMessagePromptTemplate.from_template("""CONTEXTO:
{context}

PERGUNTA: {query}

RESPOSTA:""")
])


# ============================================
# HYDE RAG PROMPTS
# ============================================

HYDE_HYPOTHETICAL_DOC_TEMPLATE = PromptTemplate(
    input_variables=["query"],
    template="""Gere um documento hipotético que responderia perfeitamente a seguinte pergunta.
O documento deve conter informações detalhadas e relevantes.

PERGUNTA: {query}

DOCUMENTO HIPOTÉTICO:"""
)

HYDE_ANSWER_TEMPLATE = PromptTemplate(
    input_variables=["context", "query"],
    template="""Baseado no contexto fornecido, responda a pergunta de forma precisa.

CONTEXTO:
{context}

PERGUNTA: {query}

RESPOSTA:"""
)


# ============================================
# RERANKING RAG PROMPTS
# ============================================

RERANKING_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["context", "query"],
    template="""Responda a pergunta usando o contexto fornecido, que já foi filtrado e reordenado por relevância.

CONTEXTO REORDENADO (do mais relevante ao menos):
{context}

PERGUNTA: {query}

INSTRUCOES:
- Use primeiramente as informações dos chunks mais relevantes (topo da lista)
- Seja preciso e objetivo
- Cite as fontes quando apropriado

RESPOSTA:"""
)


# ============================================
# AGENTIC RAG PROMPTS
# ============================================

AGENTIC_PLANNER_TEMPLATE = PromptTemplate(
    input_variables=["query"],
    template="""Analise a seguinte pergunta e crie um plano de busca.
Identifique os principais conceitos e termos que devem ser pesquisados.

PERGUNTA: {query}

PLANO DE BUSCA (liste os conceitos principais):"""
)

AGENTIC_ANSWER_TEMPLATE = PromptTemplate(
    input_variables=["context", "query", "plan"],
    template="""Você seguiu o seguinte plano de busca:
{plan}

E encontrou o seguinte contexto:
{context}

Agora responda a pergunta original de forma completa:
PERGUNTA: {query}

RESPOSTA:"""
)


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_prompt_template(technique: str) -> PromptTemplate:
    """
    Get prompt template for a specific RAG technique.

    Args:
        technique: One of 'baseline', 'hyde', 'reranking', 'agentic'

    Returns:
        PromptTemplate instance

    Example:
        >>> template = get_prompt_template('baseline')
        >>> prompt = template.format(context="...", query="...")
    """
    templates = {
        "baseline": BASELINE_RAG_TEMPLATE,
        "hyde": HYDE_ANSWER_TEMPLATE,
        "reranking": RERANKING_PROMPT_TEMPLATE,
        "agentic": AGENTIC_ANSWER_TEMPLATE,
    }

    if technique not in templates:
        raise ValueError(f"Unknown technique: {technique}. Choose from {list(templates.keys())}")

    return templates[technique]


def validate_prompt_variables(template: PromptTemplate, **kwargs) -> bool:
    """
    Validate that all required variables are provided.

    Args:
        template: PromptTemplate instance
        **kwargs: Variables to validate

    Returns:
        True if valid, raises ValueError otherwise

    Example:
        >>> validate_prompt_variables(BASELINE_RAG_TEMPLATE, context="...", query="...")
        True
    """
    missing = set(template.input_variables) - set(kwargs.keys())
    if missing:
        raise ValueError(f"Missing required variables: {missing}")
    return True
```

---

### Passo 2: Refatorar baseline_rag.py

```python
"""
Baseline RAG - Traditional RAG Implementation (Refactored)
"""

import time
from typing import Dict, List, Any

from langchain_core.documents import Document

from core.llm import get_llm
from core.embeddings import get_query_embedding_model
from core.vector_store import get_vector_store
from core.prompts import BASELINE_RAG_TEMPLATE  # ← NOVO IMPORT
from config import settings
from evaluation.ragas_eval import evaluate_rag_response


async def baseline_rag(
    query: str,
    top_k: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 500,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """Baseline RAG with PromptTemplate"""
    start_time = time.time()
    execution_details = {"technique": "baseline_rag", "steps": []}

    # ... (código de inicialização permanece igual)

    # Step 4: Build context
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

    # Step 5: Build prompt usando PromptTemplate ← MUDANÇA AQUI
    prompt = BASELINE_RAG_TEMPLATE.format(
        context=context,
        query=query
    )

    # OU usar chain pattern (mais moderno):
    # chain = BASELINE_RAG_TEMPLATE | llm
    # response = chain.invoke({"context": context, "query": query})

    # Step 6: Generate answer
    step_start = time.time()
    response = llm.invoke(prompt)
    answer = response.content

    # ... (resto do código permanece igual)

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "metrics": metrics,
        "execution_details": execution_details
    }


# Função _build_prompt() NÃO É MAIS NECESSÁRIA! 🎉
# O PromptTemplate já faz isso
```

---

### Passo 3: Exemplo de Chain Pattern (Mais Moderno)

```python
from langchain_core.runnables import RunnablePassthrough

async def baseline_rag_with_chain(
    query: str,
    top_k: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 500,
    namespace: str | None = None,
) -> Dict[str, Any]:
    """Baseline RAG usando LCEL (LangChain Expression Language)"""

    # Initialize components
    vector_store = get_vector_store(namespace=namespace)
    llm = get_llm(temperature=temperature, max_output_tokens=max_tokens)

    # Build chain: Retrieve → Format → Generate
    chain = (
        {
            "context": lambda x: "\n\n".join([
                doc.page_content
                for doc, _ in vector_store.similarity_search_with_score(x["query"], k=top_k)
            ]),
            "query": lambda x: x["query"]
        }
        | BASELINE_RAG_TEMPLATE
        | llm
    )

    # Execute chain
    response = chain.invoke({"query": query})

    return {
        "query": query,
        "answer": response.content,
        # ... rest of the response
    }
```

---

## Organização de Prompts

### Opção 1: Arquivo Único (Recomendado para projetos pequenos)

```
backend/
  core/
    prompts.py  ← Todos os prompts aqui
```

### Opção 2: Arquivo por Técnica (Recomendado para projetos grandes)

```
backend/
  prompts/
    __init__.py
    baseline.py      ← Prompts da técnica baseline
    hyde.py          ← Prompts da técnica HyDE
    reranking.py     ← Prompts da técnica reranking
    agentic.py       ← Prompts da técnica agentic
    common.py        ← Prompts compartilhados
```

**Exemplo de prompts/baseline.py**:

```python
"""Baseline RAG Prompts"""

from langchain_core.prompts import PromptTemplate

SYSTEM_INSTRUCTION = """Voce e um assistente especializado em responder perguntas baseado APENAS no contexto fornecido."""

BASELINE_TEMPLATE = PromptTemplate(
    input_variables=["context", "query"],
    template=f"""{SYSTEM_INSTRUCTION}

CONTEXTO:
{{context}}

PERGUNTA: {{query}}

INSTRUCOES:
1. Responda usando APENAS as informacoes do contexto
2. Se nao souber, diga que nao encontrou informacoes
3. Seja preciso e objetivo

RESPOSTA:"""
)
```

### Opção 3: Arquivos JSON/YAML (Máxima Flexibilidade)

```
backend/
  prompts/
    baseline.json
    hyde.json
    reranking.json
```

**baseline.json**:
```json
{
  "version": "1.0.0",
  "technique": "baseline_rag",
  "templates": {
    "main": {
      "input_variables": ["context", "query"],
      "template": "Voce e um assistente...\n\nCONTEXTO:\n{context}\n\nPERGUNTA: {query}\n\nRESPOSTA:"
    }
  }
}
```

**Carregador**:
```python
import json
from pathlib import Path
from langchain_core.prompts import PromptTemplate

def load_prompt_from_json(technique: str) -> PromptTemplate:
    """Load prompt template from JSON file"""
    path = Path(__file__).parent / "prompts" / f"{technique}.json"

    with open(path) as f:
        data = json.load(f)

    template_data = data["templates"]["main"]
    return PromptTemplate(
        input_variables=template_data["input_variables"],
        template=template_data["template"]
    )

# Uso:
template = load_prompt_from_json("baseline")
```

---

## Vantagens e Desvantagens

### ✅ Vantagens de PromptTemplate

| Vantagem | Descrição |
|----------|-----------|
| **Validação** | Detecta variáveis ausentes automaticamente |
| **Reutilização** | Use o mesmo prompt em vários lugares |
| **Versionamento** | Fácil controlar versões de prompts |
| **Testes** | Teste prompts isoladamente sem LLM |
| **Composição** | Combine templates simples em complexos |
| **Chain Pattern** | Integração com LCEL para pipelines |
| **Partial** | Preencha algumas variáveis, deixe outras para depois |
| **Formato Flexível** | Suporta f-string, jinja2, mustache |

### ❌ Desvantagens

| Desvantagem | Descrição |
|-------------|-----------|
| **Complexidade Inicial** | Mais código para setup inicial |
| **Curva de Aprendizado** | Precisa aprender API do LangChain |
| **Overhead** | Pequeno overhead de performance |
| **Dependência** | Adiciona dependência do LangChain |

---

## Aplicando em Outras Técnicas

### HyDE RAG (Hypothetical Document Embeddings)

```python
# prompts/hyde.py
from langchain_core.prompts import PromptTemplate

# Prompt 1: Gerar documento hipotético
HYDE_GENERATE_DOC = PromptTemplate(
    input_variables=["query"],
    template="""Gere um documento detalhado que responderia perfeitamente a seguinte pergunta:

PERGUNTA: {query}

DOCUMENTO HIPOTÉTICO (seja detalhado e técnico):"""
)

# Prompt 2: Responder com contexto real
HYDE_ANSWER = PromptTemplate(
    input_variables=["context", "query"],
    template="""Baseado no contexto real recuperado, responda a pergunta:

CONTEXTO:
{context}

PERGUNTA: {query}

RESPOSTA:"""
)
```

**Uso em techniques/hyde.py**:
```python
from core.prompts import HYDE_GENERATE_DOC, HYDE_ANSWER

async def hyde_rag(query: str, top_k: int = 5) -> Dict[str, Any]:
    # Step 1: Gerar documento hipotético
    llm = get_llm()
    hypothetical_doc_prompt = HYDE_GENERATE_DOC.format(query=query)
    hypothetical_doc = llm.invoke(hypothetical_doc_prompt).content

    # Step 2: Buscar usando documento hipotético
    vector_store = get_vector_store()
    retrieved_docs = vector_store.similarity_search(hypothetical_doc, k=top_k)

    # Step 3: Responder com contexto real
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    answer_prompt = HYDE_ANSWER.format(context=context, query=query)
    answer = llm.invoke(answer_prompt).content

    return {"query": query, "answer": answer, "sources": retrieved_docs}
```

---

### Reranking RAG

```python
# prompts/reranking.py
RERANKING_PROMPT = PromptTemplate(
    input_variables=["context", "query", "relevance_scores"],
    template="""Os documentos abaixo foram reordenados por relevância usando Cohere Rerank.

CONTEXTO (ordenado por relevância):
{context}

SCORES DE RELEVÂNCIA:
{relevance_scores}

PERGUNTA: {query}

INSTRUCOES:
- Priorize informações dos documentos com maior score
- Combine informações de múltiplos documentos se necessário

RESPOSTA:"""
)
```

---

### Agentic RAG

```python
# prompts/agentic.py
AGENTIC_PLANNER = PromptTemplate(
    input_variables=["query"],
    template="""Analise a pergunta e crie um plano de busca estruturado.

PERGUNTA: {query}

PLANO (liste subperguntas ou conceitos a buscar):
1.
2.
3."""
)

AGENTIC_EXECUTOR = PromptTemplate(
    input_variables=["query", "plan", "results"],
    template="""Você executou o seguinte plano:
{plan}

E obteve estes resultados:
{results}

Agora sintetize uma resposta completa para:
PERGUNTA: {query}

RESPOSTA FINAL:"""
)
```

---

## Testes de Prompts

### Teste Unitário

```python
# tests/test_prompts.py
import pytest
from core.prompts import BASELINE_RAG_TEMPLATE, validate_prompt_variables

def test_baseline_prompt_has_required_variables():
    """Testa se o prompt tem as variáveis corretas"""
    assert "context" in BASELINE_RAG_TEMPLATE.input_variables
    assert "query" in BASELINE_RAG_TEMPLATE.input_variables

def test_baseline_prompt_formatting():
    """Testa formatação do prompt"""
    context = "Python foi criado por Guido van Rossum"
    query = "Quem criou Python?"

    prompt = BASELINE_RAG_TEMPLATE.format(
        context=context,
        query=query
    )

    assert "Python foi criado por Guido van Rossum" in prompt
    assert "Quem criou Python?" in prompt
    assert "CONTEXTO:" in prompt
    assert "PERGUNTA:" in prompt

def test_prompt_validation():
    """Testa validação de variáveis"""
    # Deve passar
    validate_prompt_variables(
        BASELINE_RAG_TEMPLATE,
        context="test",
        query="test"
    )

    # Deve falhar
    with pytest.raises(ValueError, match="Missing required variables"):
        validate_prompt_variables(
            BASELINE_RAG_TEMPLATE,
            context="test"
            # query está faltando!
        )
```

### Teste de Prompt Real (com LLM)

```python
# tests/test_prompts_integration.py
import pytest
from core.llm import get_llm
from core.prompts import BASELINE_RAG_TEMPLATE

@pytest.mark.integration
async def test_baseline_prompt_with_real_llm():
    """Testa prompt com LLM real (requer API key)"""
    llm = get_llm(temperature=0.0)  # temperatura 0 para resultados determinísticos

    context = "Python é uma linguagem de programação criada por Guido van Rossum em 1991."
    query = "Quando Python foi criada?"

    prompt = BASELINE_RAG_TEMPLATE.format(context=context, query=query)
    response = llm.invoke(prompt)

    # Verifica se resposta contém a data
    assert "1991" in response.content
```

---

## Comparação de Performance

### Benchmark

```python
# scripts/benchmark_prompts.py
import time
from core.prompts import BASELINE_RAG_TEMPLATE

def benchmark_string_format():
    """Benchmark: f-string simples"""
    context = "test" * 100
    query = "test query"

    start = time.perf_counter()
    for _ in range(10000):
        prompt = f"Context: {context}\nQuery: {query}"
    end = time.perf_counter()

    return end - start

def benchmark_prompt_template():
    """Benchmark: PromptTemplate"""
    context = "test" * 100
    query = "test query"

    template = PromptTemplate(
        input_variables=["context", "query"],
        template="Context: {context}\nQuery: {query}"
    )

    start = time.perf_counter()
    for _ in range(10000):
        prompt = template.format(context=context, query=query)
    end = time.perf_counter()

    return end - start

# Resultados típicos:
# f-string: ~0.015 segundos
# PromptTemplate: ~0.025 segundos
# Diferença: ~0.01 segundos para 10,000 chamadas
# = 0.001ms por chamada (negligível!)
```

---

## Migração Gradual

### Estratégia Recomendada

**Fase 1**: Criar `core/prompts.py` com templates
- ✅ Não quebra código existente
- ✅ Adiciona apenas novos arquivos

**Fase 2**: Refatorar baseline_rag.py
- ✅ Testar e validar
- ✅ Comparar resultados com versão antiga

**Fase 3**: Implementar técnicas vazias (hyde, reranking, agentic)
- ✅ Usar PromptTemplate desde o início
- ✅ Aproveitar prompts reutilizáveis

**Fase 4**: Migrar código legado (se necessário)
- ✅ Substituir f-strings por templates
- ✅ Adicionar testes

---

## Recursos Adicionais

### Documentação LangChain
- [PromptTemplate Guide](https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/)
- [ChatPromptTemplate](https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/msg_prompt_template)
- [Few-Shot Prompts](https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/few_shot_examples)

### Exemplos Práticos
- [RAG Prompt Hub](https://smith.langchain.com/hub)
- [LangChain Templates](https://github.com/langchain-ai/langchain/tree/master/templates)

---

## Próximos Passos

1. ✅ Criar `backend/core/prompts.py`
2. ✅ Refatorar `baseline_rag.py`
3. ✅ Adicionar testes para prompts
4. ✅ Implementar HyDE com PromptTemplate
5. ✅ Implementar Reranking com PromptTemplate
6. ✅ Implementar Agentic com PromptTemplate
7. ✅ Documentar no README.md

---

**Criado em**: {datetime.now().strftime("%Y-%m-%d")}
**Projeto**: RAG Lab Backend
**Autor**: Guia Educacional
