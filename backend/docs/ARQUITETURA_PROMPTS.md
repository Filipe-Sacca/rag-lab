# 🎯 Arquitetura de Prompts - RAG Lab

## Princípio de Design

**COMPARAÇÃO JUSTA**: Todas as técnicas RAG usam o **MESMO prompt de resposta final**.

Apenas o **método de retrieval** (como os documentos são buscados) muda entre técnicas.

---

## 📊 Arquitetura Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANSWER_PROMPT (UNIVERSAL)                     │
│                                                                   │
│  Voce e um assistente especializado em responder perguntas       │
│  baseado APENAS no contexto fornecido.                           │
│                                                                   │
│  CONTEXTO: {context}                                             │
│  PERGUNTA: {query}                                               │
│                                                                   │
│  INSTRUCOES:                                                     │
│  1. Responda usando APENAS as informacoes do contexto            │
│  2. Se nao souber, diga que nao encontrou informacoes            │
│  3. Seja preciso e objetivo                                      │
│  4. Cite trechos relevantes                                      │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ USADO POR TODAS AS 4 TÉCNICAS
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   BASELINE    │      │      HYDE        │      │    RERANKING     │
│               │      │                  │      │                  │
│ 1. Embed query│      │ 1. Gerar doc hip.│      │ 1. Busca inicial │
│ 2. Search     │      │    (prompt esp.) │      │ 2. Rerank Cohere │
│ 3. Get docs   │      │ 2. Search c/ doc │      │ 3. Filter top-N  │
│               │      │ 3. Get docs      │      │                  │
│ ↓             │      │ ↓                │      │ ↓                │
│ ANSWER_PROMPT │      │ ANSWER_PROMPT    │      │ ANSWER_PROMPT    │
└───────────────┘      └──────────────────┘      └──────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │     AGENTIC      │
                        │                  │
                        │ 1. Planejar      │
                        │    (prompt esp.) │
                        │ 2. Multi-busca   │
                        │ 3. Combine docs  │
                        │ ↓                │
                        │ ANSWER_PROMPT    │
                        └──────────────────┘
```

---

## 🔑 Componentes do Sistema

### 1️⃣ ANSWER_PROMPT (Universal)
**Arquivo**: `core/prompts.py`

```python
ANSWER_PROMPT = PromptTemplate(
    input_variables=["context", "query"],
    template="""..."""  # Mesmo para TODAS as técnicas
)
```

**Usado por**:
- ✅ Baseline RAG
- ✅ HyDE RAG
- ✅ Reranking RAG
- ✅ Agentic RAG

**Garantia**: `verify_prompts_identical()` valida na importação

---

### 2️⃣ Prompts Específicos de Técnicas

**HYDE_GENERATE_DOC** (apenas HyDE):
```python
# Etapa intermediária: gerar documento hipotético
HYDE_GENERATE_DOC = PromptTemplate(
    input_variables=["query"],
    template="Gere um documento hipotetico..."
)
```

**AGENTIC_PLANNER** (apenas Agentic):
```python
# Etapa intermediária: planejar busca
AGENTIC_PLANNER = PromptTemplate(
    input_variables=["query"],
    template="Analise a pergunta e crie um plano..."
)
```

---

## 🔄 Fluxo de Cada Técnica

### Baseline RAG
```
Query do usuário
    ↓
1. Embed query
2. Search Pinecone (top_k=5)
3. Get documents
    ↓
ANSWER_PROMPT.format(context=docs, query=query)
    ↓
LLM gera resposta
```

### HyDE RAG
```
Query do usuário
    ↓
1. HYDE_GENERATE_DOC.format(query=query)
2. LLM gera documento hipotético
3. Embed documento hipotético
4. Search Pinecone com embedding do doc
5. Get documents reais
    ↓
ANSWER_PROMPT.format(context=docs, query=query)  ← MESMO PROMPT!
    ↓
LLM gera resposta
```

### Reranking RAG
```
Query do usuário
    ↓
1. Embed query
2. Search Pinecone (top_k=20, mais docs)
3. Get documents
4. Rerank com Cohere (top_k=5)
5. Filter top-N documentos
    ↓
ANSWER_PROMPT.format(context=docs, query=query)  ← MESMO PROMPT!
    ↓
LLM gera resposta
```

### Agentic RAG
```
Query do usuário
    ↓
1. AGENTIC_PLANNER.format(query=query)
2. LLM gera plano de busca
3. Múltiplas buscas baseadas no plano
4. Combine documentos de todas as buscas
    ↓
ANSWER_PROMPT.format(context=docs, query=query)  ← MESMO PROMPT!
    ↓
LLM gera resposta
```

---

## ✅ Garantias de Comparação Justa

### O que é IDÊNTICO entre técnicas:
- ✅ Prompt de geração final (`ANSWER_PROMPT`)
- ✅ LLM usado (Gemini 2.0 Flash)
- ✅ Temperature
- ✅ Max tokens
- ✅ Formato da resposta

### O que DIFERE entre técnicas:
- ❌ **Método de busca** (embedding, HyDE, reranking, agentic)
- ❌ **Número de documentos** intermediários
- ❌ **Processamento dos documentos** (filtragem, reordenação)

---

## 📝 API de Uso

### Para Implementadores de Técnicas:

```python
from core.prompts import get_answer_prompt

async def minha_tecnica_rag(query: str, top_k: int = 5):
    # 1. Recuperar documentos (método específico da técnica)
    docs = await meu_metodo_de_busca(query, top_k)

    # 2. Preparar contexto
    context = "\n\n".join([doc.page_content for doc in docs])

    # 3. Usar ANSWER_PROMPT universal (SEMPRE!)
    answer_prompt = get_answer_prompt()
    prompt = answer_prompt.format(context=context, query=query)

    # 4. Gerar resposta
    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content
```

### Para HyDE (com etapa intermediária):

```python
from core.prompts import get_hyde_doc_generator, get_answer_prompt

async def hyde_rag(query: str, top_k: int = 5):
    # Etapa 1: Gerar documento hipotético (ESPECÍFICO DO HYDE)
    doc_gen_prompt = get_hyde_doc_generator()
    hyp_doc_prompt = doc_gen_prompt.format(query=query)
    hyp_doc = llm.invoke(hyp_doc_prompt).content

    # Etapa 2: Buscar com documento hipotético
    docs = vector_store.search(hyp_doc, k=top_k)

    # Etapa 3: Responder (MESMO PROMPT DAS OUTRAS!)
    context = "\n\n".join([doc.page_content for doc in docs])
    answer_prompt = get_answer_prompt('hyde')  # Retorna ANSWER_PROMPT
    prompt = answer_prompt.format(context=context, query=query)
    response = llm.invoke(prompt)

    return response.content
```

---

## 🧪 Validação

### Teste Automático:

```python
from core.prompts import verify_prompts_identical, get_prompt_info

# Executado automaticamente na importação
verify_prompts_identical()  # Lança AssertionError se não forem iguais

# Ver informações do sistema
info = get_prompt_info()
print(info)
# {
#     'universal_prompt': True,
#     'techniques': ['baseline', 'hyde', 'reranking', 'agentic'],
#     'prompts_identical': True,
#     'design_principle': 'Todas as técnicas usam o MESMO prompt...'
# }
```

### Teste Manual:

```python
from core.prompts import get_answer_prompt

# Verificar que todas retornam o mesmo objeto
baseline_prompt = get_answer_prompt('baseline')
hyde_prompt = get_answer_prompt('hyde')
reranking_prompt = get_answer_prompt('reranking')
agentic_prompt = get_answer_prompt('agentic')

assert baseline_prompt is hyde_prompt is reranking_prompt is agentic_prompt
print("✅ Todos os prompts são idênticos!")
```

---

## 📊 Métricas de Comparação

Com prompts idênticos, as diferenças nas métricas vêm **APENAS** da técnica de retrieval:

| Métrica | O que compara |
|---------|---------------|
| **Latency** | Tempo de execução de cada técnica |
| **Faithfulness** | Fidelidade ao contexto recuperado |
| **Answer Relevancy** | Relevância da resposta à pergunta |
| **Context Precision** | Precisão dos documentos recuperados |
| **Context Recall** | Recall dos documentos recuperados |
| **Cost** | Custo em tokens (variações devido a contextos diferentes) |

---

## 🚀 Benefícios

### Para Pesquisadores:
- ✅ Comparação científica válida
- ✅ Resultados reproduzíveis
- ✅ Isolamento de variáveis

### Para Desenvolvedores:
- ✅ Prompt centralizado
- ✅ Fácil modificação (muda 1 lugar, afeta todas)
- ✅ Validação automática

### Para Usuários:
- ✅ Comparação justa entre técnicas
- ✅ Confiança nos resultados
- ✅ Escolha baseada em dados reais

---

## 🔧 Modificando o Prompt Universal

**IMPORTANTE**: Se modificar `ANSWER_PROMPT`, afeta TODAS as técnicas.

```python
# core/prompts.py

# ❌ ERRADO: Criar prompt diferente para cada técnica
BASELINE_PROMPT = PromptTemplate(...)
HYDE_PROMPT = PromptTemplate(...)  # DIFERENTE!

# ✅ CERTO: Um prompt único para todas
ANSWER_PROMPT = PromptTemplate(...)
TECHNIQUE_ANSWER_PROMPTS = {
    "baseline": ANSWER_PROMPT,  # Mesmo objeto
    "hyde": ANSWER_PROMPT,      # Mesmo objeto
    "reranking": ANSWER_PROMPT, # Mesmo objeto
    "agentic": ANSWER_PROMPT,   # Mesmo objeto
}
```

---

## 📚 Referências

- **LangChain PromptTemplate**: https://python.langchain.com/docs/modules/model_io/prompts/
- **RAG Evaluation**: https://docs.ragas.io/
- **Scientific Method**: Controle de variáveis em experimentos

---

**Criado**: 2024
**Projeto**: RAG Lab Backend
**Versão**: 1.0.0
