# Sub-Query Decomposition - Decomposição de Queries Complexas

## 📋 Definição

**Sub-Query Decomposition** é uma técnica que **quebra queries complexas em múltiplas sub-queries simples**, executa buscas independentes para cada uma, e depois **combina os resultados**.

Resolve o problema de queries que exigem informação de múltiplos contextos ou documentos diferentes.

**Insight**: Uma query complexa = várias queries simples. Buscar separadamente aumenta recall.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. DECOMPOSIÇÃO (Novo!)
   ├─ Query complexa: "Compare lucro Q3 com investimento em marketing"
   ├─ LLM decompõe em sub-queries:
   │  ├─ Sub-query 1: "Qual foi o lucro do Q3?"
   │  ├─ Sub-query 2: "Qual foi o investimento em marketing no Q3?"
   │  └─ Sub-query 3: "Relação entre lucro e marketing"
   └─ Retornar lista de sub-queries

2. RETRIEVAL PARALELO
   ├─ Para cada sub-query:
   │  ├─ Gerar embedding
   │  ├─ Buscar no Pinecone (top-k por sub-query)
   │  └─ Armazenar chunks
   └─ Combinar todos chunks (deduplicação)

3. FUSÃO (Opcional)
   ├─ Reciprocal Rank Fusion (RRF)
   ├─ Reordenar chunks combinados
   └─ Selecionar top-k final

4. GERAÇÃO
   ├─ Montar prompt com chunks de TODAS sub-queries
   ├─ LLM sintetiza resposta completa
   └─ Retornar resposta final
```

### Comparação Visual

**Baseline RAG:**
```
Query complexa → Busca única → 5 chunks (incompletos)
```

**Sub-Query:**
```
Query complexa
    ↓ [Decompõe]
Sub-query 1 → Busca → 5 chunks
Sub-query 2 → Busca → 5 chunks
Sub-query 3 → Busca → 5 chunks
    ↓ [Combina]
15 chunks → Deduplica/Fusiona → 10 chunks finais
```

---

## 💡 Por Que Funciona?

### Problema do Baseline

```python
Query: "Compare lucro Q3 com investimento em marketing e analise ROI"

# Embedding da query (mistura 3 conceitos):
query_vector = embed("Compare lucro Q3 com investimento marketing analise ROI")

# Busca retorna (confuso):
Chunk 1: "Lucro Q3: R$ 3bi..."              ✅ (parcial)
Chunk 2: "Marketing digital cresceu..."      ✅ (parcial)
Chunk 3: "Estratégia de marketing..."        ❌ (genérico)
Chunk 4: "ROI de investimentos gerais..."    ❌ (não específico)
Chunk 5: "Resultado financeiro Q3..."        ✅ (parcial)

# ❌ Nenhum chunk tem informação completa
# ❌ Falta chunk específico sobre "investimento marketing Q3"
```

### Solução Sub-Query

```python
# LLM decompõe:
sub_queries = [
    "Qual foi o lucro do terceiro trimestre?",
    "Qual foi o investimento em marketing no terceiro trimestre?",
    "Como calcular ROI de marketing?"
]

# Busca 1 (foco: lucro):
chunks_1 = search("lucro terceiro trimestre", k=5)
→ "Lucro Q3: R$ 3bi, crescimento 15%..."     ✅

# Busca 2 (foco: marketing):
chunks_2 = search("investimento marketing terceiro trimestre", k=5)
→ "Investimento marketing Q3: R$ 500mi..."   ✅

# Busca 3 (foco: ROI):
chunks_3 = search("calcular ROI marketing", k=5)
→ "ROI = (Receita - Custo) / Custo..."       ✅

# Combina todos chunks:
final_chunks = deduplicate(chunks_1 + chunks_2 + chunks_3)
→ 12 chunks únicos, TODOS relevantes

# ✅ Informação completa para resposta
```

**Resultado**: Context Recall de 0.50 → 0.85

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query Multi-Hop

**Query:**
```
"Quem é o CFO e qual sua experiência anterior em finanças?"
```

**Baseline (Falha):**
```python
# Busca única com query completa
results = search("CFO experiência anterior finanças")

# Chunks recuperados (incompletos):
1. "Nosso CFO é João Silva..."               ✅ (nome)
2. "Equipe de liderança inclui CFO..."       ❌ (genérico)
3. "Experiência em finanças corporativas..." ❌ (não vincula ao CFO)
4. "João Silva foi promovido..."             ❌ (não menciona experiência)

# ❌ Tem o nome, mas não tem a experiência dele
```

**Sub-Query (Sucesso):**
```python
# Decomposição:
sub_1 = "Quem é o CFO da empresa?"
sub_2 = "Qual a experiência anterior do CFO?"

# Busca 1 (identifica pessoa):
chunks_1 = search(sub_1, k=5)
→ "CFO: João Silva, formado em Harvard..."   ✅

# Busca 2 (com contexto de "CFO"):
chunks_2 = search(sub_2, k=5)
→ "João Silva trabalhou 10 anos no Goldman Sachs..." ✅

# LLM sintetiza:
"O CFO é João Silva. Ele possui 10 anos de experiência
 no Goldman Sachs antes de se juntar à empresa."

# ✅ Resposta completa conectando ambas as informações
```

---

### Caso 2: Comparação Entre Entidades

**Query:**
```
"Compare o desempenho de vendas de 2023 vs 2024"
```

**Baseline (Incompleto):**
```python
results = search("vendas 2023 vs 2024")

# Chunks (podem não ter ambos os anos):
1. "Vendas 2024: R$ 10mi, crescimento..."    ✅ (2024)
2. "Performance de vendas melhorou..."       ❌ (vago)
3. "Vendas 2023: R$ 8mi..."                  ✅ (2023)

# ❌ Tem dados, mas não focados na comparação
```

**Sub-Query (Completo):**
```python
sub_1 = "Qual foi o desempenho de vendas em 2023?"
sub_2 = "Qual foi o desempenho de vendas em 2024?"
sub_3 = "Qual a diferença percentual entre vendas 2023 e 2024?"

# Busca focada por ano:
chunks_1 = search(sub_1, k=3)  # Só 2023
chunks_2 = search(sub_2, k=3)  # Só 2024
chunks_3 = search(sub_3, k=3)  # Análise comparativa

# Resultado: Dados completos de ambos períodos + análise
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Max Sub-Queries** | 3-5 | Balance entre recall e latência |
| **Top-K per Sub-Query** | 3-5 | Evita explosão de chunks |
| **Deduplication** | Sim | Remove chunks duplicados |
| **Fusion Method** | RRF | Combina rankings de forma justa |
| **LLM (Decomposition)** | Gemini 2.5 Flash | Rápido para decomposição |
| **Temperature** | 0.0 | Decomposição determinística |

---

## ✅ Vantagens

### 1. Recall Massivo
```
Baseline: 1 busca → 5 chunks → Recall 0.50
Sub-Query: 3 buscas → 15 chunks → Recall 0.85 (+70%)
```

### 2. Queries Multi-Hop Resolvidas
```
✅ "Quem é X e qual sua posição em Y?"
✅ "Compare A com B em termos de C"
✅ "Relacione evento X com impacto em Y"
```

### 3. Cobertura de Múltiplos Documentos
```
Query complexa pode precisar:
- Doc financeiro (lucro)
- Doc marketing (investimento)
- Doc estratégico (análise)

Sub-queries garantem busca em TODOS
```

### 4. Precisão por Contexto
```
Cada sub-query é simples e focada:
→ Embedding mais preciso
→ Busca mais direcionada
→ Menos ruído
```

### 5. Transparência e Debug
```
Pode ver exatamente:
- Quais sub-queries foram geradas
- Que chunks cada uma retornou
- Como foram combinados

Facilita identificar falhas
```

---

## ❌ Desvantagens

### 1. Latência Alta
```
Baseline: 1 busca = 1.2s
Sub-Query: 3 buscas = 2.5-4.0s

Breakdown:
- Decomposição: +0.5s (LLM)
- 3x buscas: +1.0s (paralelo) ou +2.0s (sequencial)
- Fusão: +0.3s
- Geração: 1.0s
```

### 2. Custo Elevado
```
# Chamadas LLM:
1. Decomposição (gerar sub-queries)
2. Geração final (resposta)

# Buscas vetoriais:
3x buscas no Pinecone (vs 1x baseline)

Custo: $0.004-0.008 por query (+200-300%)
```

### 3. Risco de Over-Decomposition
```
Query simples: "Qual o telefone?"

❌ LLM pode decompor desnecessariamente:
- "Número de telefone da empresa"
- "Código de área do telefone"
- "Tipo de telefone (fixo/móvel)"

→ Overhead sem benefício
```

### 4. Combinação Complexa
```
15 chunks de 3 sub-queries:
- Como priorizar?
- Como evitar informação conflitante?
- Qual chunk é mais importante?

Fusion (RRF) ajuda, mas não é perfeito
```

### 5. Context Window Explodir
```
3 sub-queries × 5 chunks = 15 chunks
15 chunks × 512 tokens = 7,680 tokens

Se chunk size = 1024:
15 × 1024 = 15,360 tokens (pode exceder limite LLM!)

Precisa limitar top-k ou comprimir chunks
```

### 6. Dependência de Decomposição
```
Se LLM decompõe MAL:
❌ Sub-queries irrelevantes
❌ Perde aspecto importante da query original
❌ Busca em direção errada

Qualidade da decomposição = crítica
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline | Sub-Query | Δ |
|---------|----------|-----------|---|
| **Faithfulness** | 0.75-0.85 | 0.80-0.88 | +5-10% |
| **Answer Relevancy** | 0.70-0.85 | 0.75-0.90 | +5-15% |
| **Context Precision** | 0.60-0.75 | 0.65-0.80 | +5-10% |
| **Context Recall** | 0.50-0.70 | 0.75-0.90 | +40-60% ⭐ |

### Performance

| Métrica | Baseline | Sub-Query |
|---------|----------|-----------|
| **Latência** | 1.2-2.5s | 2.5-4.5s |
| **Custo/Query** | $0.001-0.003 | $0.004-0.010 |
| **Chunks Retrieved** | 5 | 10-15 (deduplicated) |
| **Throughput** | ~40 q/min | ~15-20 q/min |

---

## 🎯 Quando Usar Sub-Query

### ✅ Casos Ideais

**1. Queries Multi-Hop**
```
✅ "Quem é o CEO e qual sua formação acadêmica?"
✅ "Produto X foi lançado quando e quais foram as vendas?"
✅ "Relacione evento A com impacto em B"
```

**2. Comparações**
```
✅ "Compare vendas 2023 vs 2024"
✅ "Diferença entre plano básico e premium"
✅ "Produto A vs Produto B: qual melhor?"
```

**3. Agregação de Múltiplos Contextos**
```
✅ "Análise completa: financeiro + operacional + estratégico"
✅ "Resumo de todos departamentos sobre projeto X"
```

**4. Queries com Múltiplas Partes**
```
✅ "Política de férias, benefícios E processo de avaliação"
✅ "Preço, especificações técnicas E disponibilidade do produto"
```

**5. Análises Complexas**
```
✅ "Impacto do investimento em P&D no crescimento de receita"
✅ "Correlação entre satisfação do cliente e retenção"
```

---

### ❌ Quando NÃO Usar

**1. Queries Simples e Diretas**
```
❌ "Qual o telefone?"
❌ "Email do suporte"
❌ "Horário de funcionamento"
→ Baseline é suficiente e 2x mais rápido
```

**2. Lookup Factual**
```
❌ "Preço do produto X"
❌ "Data de lançamento"
→ Não precisa de múltiplas buscas
```

**3. Latência Crítica**
```
❌ Requisitos de <2s resposta
❌ Chatbot em tempo real
→ Sub-Query pode levar 4-5s
```

**4. Vector DB Pequeno**
```
❌ <1K documentos
→ Busca única já cobre tudo
→ Sub-queries = overhead desnecessário
```

**5. Budget Apertado**
```
❌ Custo 3x do baseline
❌ Alto volume de queries (>50K/dia)
→ Pode ficar caro rapidamente
```

---

## 🔬 Experimentos Recomendados

### 1. Number of Sub-Queries
```python
# Testar: 2, 3, 5, 7 sub-queries
# Medir: Recall vs Latência
# Hipótese: 3-4 sub-queries = sweet spot
```

### 2. Top-K per Sub-Query
```python
# Testar: k=3, k=5, k=10 por sub-query
# Medir: Recall vs Context Window overflow
# Hipótese: k=3-5 balanceia cobertura e tokens
```

### 3. Fusion Method Comparison
```python
# Testar:
# - Simple concatenation
# - Reciprocal Rank Fusion (RRF)
# - Weighted fusion (sub-query importance)
# Medir: Precision + Recall
```

### 4. Parallel vs Sequential Retrieval
```python
# Parallel: Executar todas buscas simultaneamente
# Sequential: Uma por vez
# Medir: Latência (parallel deve ser ~40% mais rápido)
```

---

## 💻 Estrutura de Código

```python
# subquery.py

import asyncio
from typing import List

class SubQueryRAG:
    """
    RAG com decomposição de queries complexas.

    Pipeline:
    1. Decomposição em sub-queries
    2. Retrieval paralelo para cada sub-query
    3. Fusão de resultados (RRF)
    4. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm):
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm
        self.k_per_subquery = 5
        self.max_subqueries = 4

    def decompose(self, query: str) -> List[str]:
        """
        Decompõe query complexa em sub-queries.
        """
        prompt = f"""
Você é um assistente que decompõe queries complexas.

Query original: "{query}"

Decomponha esta query em 2-4 sub-queries SIMPLES e FOCADAS.
Cada sub-query deve buscar um aspecto específico da informação.

Regras:
- Máximo 4 sub-queries
- Cada uma deve ser independente
- Cobrir todos aspectos da query original
- Se query é simples, retorne apenas 1 (a original)

Retorne apenas as sub-queries, uma por linha, sem numeração:
"""
        response = self.llm.invoke(prompt, temperature=0.0)

        # Parse sub-queries (separadas por linha)
        sub_queries = [
            sq.strip()
            for sq in response.content.split('\n')
            if sq.strip() and not sq.strip().startswith('#')
        ]

        # Limitar máximo
        return sub_queries[:self.max_subqueries]

    async def retrieve_single(self, sub_query: str) -> List[Document]:
        """
        Busca para uma única sub-query.
        """
        query_vector = self.embeddings.embed_query(sub_query)

        results = self.index.query(
            vector=query_vector,
            top_k=self.k_per_subquery,
            include_metadata=True
        )

        chunks = self._parse_results(results)

        # Adicionar metadata de qual sub-query recuperou
        for chunk in chunks:
            chunk.metadata['source_subquery'] = sub_query

        return chunks

    async def retrieve_parallel(self, sub_queries: List[str]) -> List[Document]:
        """
        Retrieval paralelo para todas sub-queries.
        """
        # Executar todas buscas em paralelo
        tasks = [self.retrieve_single(sq) for sq in sub_queries]
        results = await asyncio.gather(*tasks)

        # Combinar todos chunks
        all_chunks = []
        for chunks in results:
            all_chunks.extend(chunks)

        return all_chunks

    def deduplicate(self, chunks: List[Document]) -> List[Document]:
        """
        Remove chunks duplicados (mesmo conteúdo).
        """
        seen = set()
        unique_chunks = []

        for chunk in chunks:
            content_hash = hash(chunk.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_chunks.append(chunk)

        return unique_chunks

    def reciprocal_rank_fusion(
        self,
        chunks: List[Document],
        k: int = 60
    ) -> List[Document]:
        """
        Fusão usando Reciprocal Rank Fusion.

        RRF score = Σ 1/(k + rank_in_subquery_i)
        """
        # Agrupar chunks por sub-query fonte
        subquery_rankings = {}
        for chunk in chunks:
            sq = chunk.metadata.get('source_subquery', 'unknown')
            if sq not in subquery_rankings:
                subquery_rankings[sq] = []
            subquery_rankings[sq].append(chunk)

        # Calcular RRF score para cada chunk
        rrf_scores = {}
        for chunk in chunks:
            score = 0.0
            for sq, ranked_chunks in subquery_rankings.items():
                # Encontrar rank deste chunk nesta sub-query
                try:
                    rank = ranked_chunks.index(chunk)
                    score += 1.0 / (k + rank)
                except ValueError:
                    # Chunk não veio desta sub-query
                    pass

            rrf_scores[id(chunk)] = score
            chunk.metadata['rrf_score'] = score

        # Reordenar por RRF score
        sorted_chunks = sorted(
            chunks,
            key=lambda x: rrf_scores[id(x)],
            reverse=True
        )

        return sorted_chunks

    def generate(self, query: str, context: List[Document]) -> str:
        """
        Geração com LLM.
        """
        prompt = self._build_prompt(query, context)
        response = self.llm.invoke(prompt, temperature=0.0)
        return response.content

    def query(self, query: str) -> dict:
        """
        Pipeline completo.
        """
        start_time = time.time()

        # 1. Decomposição
        t1 = time.time()
        sub_queries = self.decompose(query)
        decompose_time = time.time() - t1

        # 2. Retrieval paralelo
        t2 = time.time()
        all_chunks = asyncio.run(self.retrieve_parallel(sub_queries))
        retrieval_time = time.time() - t2

        # 3. Deduplicação
        unique_chunks = self.deduplicate(all_chunks)

        # 4. Fusão (RRF)
        t3 = time.time()
        fused_chunks = self.reciprocal_rank_fusion(unique_chunks)
        fusion_time = time.time() - t3

        # Selecionar top-10 finais
        final_chunks = fused_chunks[:10]

        # 5. Geração
        t4 = time.time()
        response = self.generate(query, final_chunks)
        generation_time = time.time() - t4

        total_latency = time.time() - start_time

        return {
            "response": response,
            "chunks": final_chunks,
            "sub_queries": sub_queries,
            "metrics": {
                "latency_total": total_latency,
                "latency_decompose": decompose_time,
                "latency_retrieval": retrieval_time,
                "latency_fusion": fusion_time,
                "latency_generation": generation_time,
                "num_subqueries": len(sub_queries),
                "chunks_total": len(all_chunks),
                "chunks_unique": len(unique_chunks),
                "chunks_final": len(final_chunks),
                "technique": "subquery"
            }
        }
```

---

## 🎓 Variações Avançadas

### 1. Adaptive Sub-Query
```python
def adaptive_subquery(query):
    """
    Decide automaticamente se decompor ou não.
    """
    # Classificar complexidade
    complexity = classify_complexity(query)

    if complexity == "simple":
        return baseline_rag(query)
    elif complexity == "medium":
        return subquery_rag(query, max_subqueries=2)
    else:  # complex
        return subquery_rag(query, max_subqueries=4)
```

---

### 2. Hierarchical Sub-Query
```python
def hierarchical_subquery(query):
    """
    Sub-queries podem gerar sub-sub-queries.
    """
    # Nível 1
    sub_queries_l1 = decompose(query)

    # Nível 2 (apenas para sub-queries complexas)
    all_subqueries = []
    for sq in sub_queries_l1:
        if is_complex(sq):
            sub_queries_l2 = decompose(sq)
            all_subqueries.extend(sub_queries_l2)
        else:
            all_subqueries.append(sq)

    # Retrieval
    chunks = retrieve_parallel(all_subqueries)
    return chunks
```

---

### 3. Sub-Query + Reranking
```python
def subquery_with_reranking(query):
    """
    Combina recall de sub-query com precision de reranking.
    """
    # 1. Sub-query retrieval (alto recall)
    sub_queries = decompose(query)
    chunks = retrieve_parallel(sub_queries, k=10)  # 3×10=30 chunks

    # 2. Deduplica
    unique = deduplicate(chunks)  # ~20 chunks

    # 3. Reranking (alta precision)
    final = rerank(query, unique, k=5)  # Top-5

    return final
```

**Benefício**: Recall 0.90 + Precision 0.95 = Best of both worlds

---

## 📚 Referências

**Papers:**
- Khattab et al. (2022) - "Demonstrate-Search-Predict: Composing retrieval and language models"
- Press et al. (2023) - "Measuring and Narrowing the Compositionality Gap in Language Models"

**Implementações:**
- LangChain: `MultiQueryRetriever`
- LlamaIndex: `SubQuestionQueryEngine`

**Benchmarks:**
- HotpotQA (multi-hop): +25% EM vs single query
- 2WikiMultihopQA: +18% F1

---

## 🎯 Aprendizados Chave

1. **Recall é Rei**: Sub-Query maximiza recall em queries complexas
2. **Decomposição = Crítico**: Qualidade das sub-queries define sucesso
3. **Paralelo Essential**: Retrieval paralelo reduz latência em 50%
4. **Fusão Matters**: RRF combina rankings de forma justa
5. **Combina com Reranking**: Recall (Sub-Query) + Precision (Reranking) = perfeito

---

## 📈 Progressão de Complexidade

```
Baseline RAG (single query)
    ↓
Sub-Query (você está aqui)
    ↓
    ├─→ Adaptive Sub-Query (auto-decide)
    ├─→ Hierarchical (sub-sub-queries)
    └─→ Sub-Query + Reranking (combo perfeito)
```

---

**Técnica Anterior**: [Reranking](./RERANKING.md)
**Próxima Técnica**: [Fusion](./FUSION.md)
