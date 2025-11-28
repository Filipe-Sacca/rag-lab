# Fusion - Combinação de Múltiplas Estratégias de Retrieval

## 📋 Definição

**Fusion** (também chamado de **RAG Fusion** ou **Hybrid Retrieval**) é uma meta-técnica que **combina resultados de múltiplas estratégias de busca diferentes** para maximizar tanto recall quanto precision.

A ideia é que diferentes métodos de busca capturam aspectos complementares da relevância.

**Insight**: Nenhuma técnica é perfeita. Combinar várias técnicas cancela fraquezas e amplifica forças.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. QUERY AUGMENTATION (Preparação)
   ├─ Query original: "Qual o lucro Q3?"
   ├─ Gerar variações da query:
   │  ├─ Variação 1: Original
   │  ├─ Variação 2: Reformulada (LLM)
   │  ├─ Variação 3: Com sinônimos
   │  └─ Variação 4: Mais específica
   └─ Total: 3-5 variações

2. MULTI-STRATEGY RETRIEVAL (Busca Paralela)
   ├─ Para cada variação, executar:
   │  ├─ Busca Semântica (Vector DB)
   │  ├─ Busca Lexical (BM25/Keyword)
   │  └─ Busca Híbrida (Semantic + Lexical)
   └─ Resultado: Múltiplos conjuntos de chunks

3. FUSION (Combinação) ⭐
   ├─ Reciprocal Rank Fusion (RRF)
   │  └─ Score = Σ 1/(k + rank_in_list_i)
   ├─ Combinar rankings de todas estratégias
   └─ Reordenar chunks por score final

4. GERAÇÃO
   ├─ Selecionar top-k chunks fusionados
   ├─ Montar prompt
   └─ LLM gera resposta
```

### Comparação Visual

**Baseline RAG:**
```
Query → Busca Semântica → 5 chunks
```

**Fusion:**
```
Query
  ↓ [Gera variações]
Q1, Q2, Q3
  ↓ [Múltiplas estratégias]
Q1 → Semântica → 10 chunks
Q1 → Lexical  → 10 chunks
Q2 → Semântica → 10 chunks
Q2 → Lexical  → 10 chunks
Q3 → Semântica → 10 chunks
  ↓ [Fusão RRF]
50 chunks → Dedup → RRF → Top 10
```

---

## 💡 Por Que Funciona?

### Complementaridade de Estratégias

**Busca Semântica (Vector):**
- ✅ Captura sinônimos e contexto
- ✅ Entende intenção semântica
- ❌ Falha em keywords exatos
- ❌ Sensível a vocabulário

**Busca Lexical (BM25):**
- ✅ Match exato de keywords
- ✅ Funciona com nomes próprios
- ❌ Não entende sinônimos
- ❌ Não captura contexto

**Fusão = Melhor dos Dois Mundos:**
```python
Query: "CEO da Apple"

# Semântica:
Chunk 1: "Tim Cook lidera a Apple..."        Score: 0.92 ✅
Chunk 2: "Diretor executivo da Apple..."     Score: 0.85 ✅ (sinônimo)

# Lexical (BM25):
Chunk 1: "CEO Apple: Tim Cook..."            Score: 0.95 ✅ (keyword exato)
Chunk 3: "Apple CEO anunciou..."             Score: 0.88 ✅

# Fusion (RRF):
Chunk 1: Alta em AMBAS → RRF = 0.98 ⭐ (melhor)
Chunk 2: Alta em semântica → RRF = 0.75
Chunk 3: Alta em lexical → RRF = 0.72

# ✅ Chunk 1 (que aparece bem em ambas) ganha
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query com Nome Próprio

**Query:**
```
"Política de trabalho remoto da empresa XYZ Corp"
```

**Semântica Sozinha (Perde Nome):**
```python
# Embedding captura "política trabalho remoto"
# Mas pode não priorizar "XYZ Corp" especificamente

Chunks:
1. "Política remoto: 3 dias/semana..." (genérico)    0.88
2. "XYZ Corp permite trabalho flexível..."           0.75 (baixo!)
3. "Trabalho remoto em empresas tech..."             0.82
```

**Lexical Sozinha (Perde Contexto):**
```python
# BM25 busca keywords "XYZ Corp" "trabalho remoto"

Chunks:
1. "XYZ Corp sede localizada..."                     0.90 (tem "XYZ" mas não é política)
2. "XYZ Corp permite trabalho flexível..."           0.85 ✅
3. "Política remoto na empresa ABC..."               0.70 (não é XYZ)
```

**Fusion (Combina Forças):**
```python
# RRF combina rankings:

Chunk "XYZ Corp permite trabalho flexível...":
  - Semântica: Rank 2 → 1/(60+2) = 0.016
  - Lexical:   Rank 1 → 1/(60+1) = 0.016
  - RRF = 0.032 ⭐ (soma = melhor score)

Chunk "Política remoto: 3 dias/semana...":
  - Semântica: Rank 1 → 1/(60+1) = 0.016
  - Lexical:   Rank 5 → 1/(60+5) = 0.015
  - RRF = 0.031

# ✅ Chunk correto (XYZ + remoto) vence!
```

---

### Caso 2: Query Variations Power

**Query Original:**
```
"Como melhorar performance do sistema?"
```

**Variações Geradas:**
```
V1: "Como melhorar performance do sistema?"          (original)
V2: "Otimização de desempenho de aplicações"         (reformulada)
V3: "Reduzir latência e aumentar throughput"         (específica)
V4: "Melhorar velocidade processamento sistema"      (sinônimos)
```

**Resultado:**
```python
# Cada variação captura chunks diferentes:

V1 → "Performance sistema: cache Redis..."           ✅
V2 → "Otimização aplicações: indexação DB..."        ✅
V3 → "Reduzir latência: CDN e compressão..."         ✅
V4 → "Velocidade: paralelização processos..."        ✅

# Fusão garante cobertura completa de todas perspectivas
# Recall massivo: 0.50 → 0.90
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Query Variations** | 3-4 | Balance recall vs latência |
| **Retrieval Strategies** | 2 (Semantic + BM25) | Complementares |
| **Top-K per Strategy** | 10 | Captura diversidade |
| **Fusion Method** | RRF (k=60) | Padrão da literatura |
| **Final Top-K** | 10 | Suficiente para LLM |
| **Deduplication** | Sim | Remove duplicatas |

### Estratégias de Retrieval Comuns

| Estratégia | Método | Uso |
|------------|--------|-----|
| **Semantic** | Vector DB (embeddings) | Contexto, sinônimos |
| **Lexical** | BM25, TF-IDF | Keywords exatas |
| **Hybrid** | Weighted combination | Balance |
| **HyDE** | Hypothetical embeddings | Queries abertas |
| **Multi-Query** | Query variations | Cobertura |

---

## ✅ Vantagens

### 1. Recall + Precision Simultâneos
```
Baseline:
- Alta precision OU alto recall (não ambos)

Fusion:
- Recall: 0.85-0.95 (query variations)
- Precision: 0.85-0.90 (RRF filtra ruído)
```

### 2. Robustez a Diferentes Queries
```
✅ Queries com keywords → Lexical ajuda
✅ Queries semânticas → Vector ajuda
✅ Queries mistas → Fusion equilibra
```

### 3. Cancela Fraquezas Individuais
```
Semantic falha em keyword exato
→ Lexical compensa

Lexical falha em sinônimos
→ Semantic compensa

Fusion = Safety net
```

### 4. Escalabilidade de Estratégias
```python
# Adicionar novas estratégias facilmente:
strategies = [
    semantic_search,
    bm25_search,
    hyde_search,
    graph_search,
    custom_search
]

# Fusion combina TODAS automaticamente
```

### 5. State-of-the-Art Results
```
BEIR benchmark: Fusion = top 3 técnicas
Melhor que qualquer técnica individual
```

---

## ❌ Desvantagens

### 1. Latência Extrema
```
Baseline: 1.2s
Fusion: 3.5-6.0s

Breakdown:
- 4 query variations: +0.8s (LLM)
- 2 strategies × 4 queries = 8 buscas: +2.0s
- Fusion (RRF): +0.5s
- Geração: 1.2s

Total: 4-6 segundos
```

### 2. Custo Massivo
```
# LLM calls:
1. Gerar query variations (4x)
2. Geração final
Total: 5 LLM calls vs 1 baseline

# Vector DB:
8 buscas vs 1 baseline

Custo: $0.010-0.020 por query (+500-1000%!)
```

### 3. Complexidade Implementação
```
Precisa implementar/integrar:
- Vector DB (Pinecone)
- BM25 engine (Elasticsearch ou local)
- Query variation generator
- RRF algorithm
- Deduplication logic

Complexidade operacional alta
```

### 4. Deduplicação Imperfeita
```
Mesmo chunk pode aparecer em múltiplas buscas:

Busca 1: "Lucro Q3 foi R$ 3bi..."
Busca 2: "Lucro Q3 foi R$ 3 bi..." (formatação diferente)

❌ Dedup por hash falha (texto diferente)
→ Chunks duplicados inflam context window
```

### 5. RRF Pode Não Ser Ótimo
```
RRF assume todas estratégias têm peso igual

Mas:
- Semantic pode ser 2x melhor que BM25
- Deveria ter peso maior

Weighted fusion resolve, mas precisa tuning
```

### 6. Não Funciona Para Queries Simples
```
Query: "Telefone"

❌ Query variations inúteis:
- "Telefone"
- "Número de telefone"
- "Contato telefônico"

❌ Múltiplas estratégias retornam mesmo chunk
→ Overhead sem benefício
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline | Fusion | Δ |
|---------|----------|--------|---|
| **Faithfulness** | 0.75-0.85 | 0.85-0.92 | +10-15% |
| **Answer Relevancy** | 0.70-0.85 | 0.88-0.95 | +20-25% |
| **Context Precision** | 0.60-0.75 | 0.85-0.92 | +30-40% |
| **Context Recall** | 0.50-0.70 | 0.85-0.95 | +50-70% ⭐ |

### Performance

| Métrica | Baseline | Fusion |
|---------|----------|--------|
| **Latência** | 1.2-2.5s | 3.5-6.5s |
| **Custo/Query** | $0.001-0.003 | $0.010-0.025 |
| **Chunks Retrieved** | 5 | 15-25 (deduplicated) |
| **Throughput** | ~40 q/min | ~10-15 q/min |

---

## 🎯 Quando Usar Fusion

### ✅ Casos Ideais

**1. Máxima Qualidade Necessária**
```
✅ Research assistants (academia)
✅ Legal/compliance (zero margem erro)
✅ Medical diagnosis support
```

**2. Queries Diversas e Imprevisíveis**
```
✅ Chat geral (não sabe tipo de query)
✅ Multi-domain knowledge base
✅ User queries em linguagem natural variada
```

**3. Benchmark e Competições**
```
✅ Comparar com state-of-the-art
✅ Demonstrar capabilities
✅ Provar viabilidade técnica
```

**4. Baixo Volume, Alta Criticidade**
```
✅ <1K queries/dia
✅ Budget OK com $10-20/dia
✅ Cada resposta vale muito (decisões críticas)
```

**5. Cobrir Múltiplas Modalidades**
```
✅ Código + documentação + logs
✅ Dados estruturados + texto livre
✅ Multi-idioma
```

---

### ❌ Quando NÃO Usar

**1. Produção em Escala**
```
❌ >10K queries/dia
❌ Custo seria $200-500/dia
❌ Latência 5s inaceitável para UX
```

**2. Queries Simples e Previsíveis**
```
❌ FAQ system (queries repetitivas)
❌ Lookup database (queries diretas)
→ Baseline 5x mais rápido e barato
```

**3. Budget Limitado**
```
❌ Custo 10x baseline
❌ Startups early-stage
→ Use técnicas individuais otimizadas
```

**4. Latência Crítica**
```
❌ Real-time chat (<2s)
❌ Autocomplete (<500ms)
❌ API com SLA <1s
```

**5. Infraestrutura Simples**
```
❌ Só tem Vector DB (sem BM25)
❌ Não quer manter múltiplos sistemas
→ Use Reranking ou HyDE
```

---

## 🔬 Experimentos Recomendados

### 1. Strategy Combination Testing
```python
# Testar combinações:
# - Semantic only
# - Semantic + BM25
# - Semantic + BM25 + HyDE
# - Todas estratégias

# Medir: Recall vs Latência vs Custo
```

### 2. Query Variation Count
```python
# Testar: 1, 2, 3, 5, 10 variations
# Medir: Recall improvement vs Latência
# Hipótese: 3-4 variations = sweet spot
```

### 3. Fusion Algorithm Comparison
```python
# Testar:
# - Simple voting (count)
# - RRF (reciprocal rank)
# - Weighted fusion (tuned weights)
# - Learned fusion (ML model)

# Medir: Precision + Recall
```

### 4. Top-K Optimization
```python
# Per strategy: Testar k=5, 10, 20, 50
# Final: Testar k=5, 10, 15, 20
# Medir: Recall vs Context Window size
```

---

## 💻 Estrutura de Código

```python
# fusion.py

import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Dict

class FusionRAG:
    """
    RAG Fusion: Combina múltiplas estratégias de retrieval.

    Pipeline:
    1. Query variations
    2. Multi-strategy retrieval
    3. Reciprocal Rank Fusion
    4. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm, bm25_corpus=None):
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm

        # BM25 para busca lexical
        self.bm25 = None
        if bm25_corpus:
            self.bm25 = BM25Okapi(bm25_corpus)

        self.num_variations = 3
        self.k_per_strategy = 10

    def generate_query_variations(self, query: str) -> List[str]:
        """
        Gera variações da query para aumentar recall.
        """
        prompt = f"""
Gere 3 variações diferentes da query abaixo.
Cada variação deve:
- Usar sinônimos e reformulações
- Manter a intenção original
- Ser mais específica ou usar termos técnicos

Query original: "{query}"

Retorne apenas as 3 variações, uma por linha:
"""
        response = self.llm.invoke(prompt, temperature=0.7)

        variations = [query]  # Incluir original
        variations.extend([
            v.strip()
            for v in response.content.split('\n')
            if v.strip() and not v.strip().startswith('#')
        ][:3])

        return variations

    def semantic_search(self, query: str, k: int) -> List[Document]:
        """
        Busca semântica (vector DB).
        """
        query_vector = self.embeddings.embed_query(query)

        results = self.index.query(
            vector=query_vector,
            top_k=k,
            include_metadata=True
        )

        chunks = self._parse_results(results)

        # Marcar estratégia
        for chunk in chunks:
            chunk.metadata['strategy'] = 'semantic'

        return chunks

    def lexical_search(self, query: str, k: int) -> List[Document]:
        """
        Busca lexical (BM25).
        """
        if not self.bm25:
            return []

        # Tokenizar query
        query_tokens = query.lower().split()

        # BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Top-k indices
        top_indices = np.argsort(scores)[::-1][:k]

        chunks = [self.corpus_docs[i] for i in top_indices]

        # Marcar estratégia
        for chunk, score in zip(chunks, scores[top_indices]):
            chunk.metadata['strategy'] = 'lexical'
            chunk.metadata['bm25_score'] = float(score)

        return chunks

    def multi_strategy_retrieval(
        self,
        query_variations: List[str]
    ) -> List[List[Document]]:
        """
        Executa múltiplas estratégias para cada variação.
        """
        all_results = []

        for query_var in query_variations:
            # Semantic
            semantic_chunks = self.semantic_search(query_var, self.k_per_strategy)
            all_results.append(semantic_chunks)

            # Lexical
            if self.bm25:
                lexical_chunks = self.lexical_search(query_var, self.k_per_strategy)
                all_results.append(lexical_chunks)

        return all_results

    def reciprocal_rank_fusion(
        self,
        ranked_lists: List[List[Document]],
        k: int = 60
    ) -> List[Document]:
        """
        Fusão usando Reciprocal Rank Fusion.

        RRF(d) = Σ 1/(k + rank(d) in list_i)
        """
        # Coletar todos chunks únicos
        all_chunks = []
        for ranked_list in ranked_lists:
            all_chunks.extend(ranked_list)

        # Deduplicar por conteúdo
        unique_chunks = {}
        for chunk in all_chunks:
            content_hash = hash(chunk.page_content)
            if content_hash not in unique_chunks:
                unique_chunks[content_hash] = chunk

        # Calcular RRF score para cada chunk único
        rrf_scores = {}

        for content_hash, chunk in unique_chunks.items():
            score = 0.0

            # Somar contribuição de cada ranked list
            for ranked_list in ranked_lists:
                try:
                    # Encontrar posição deste chunk nesta lista
                    for rank, c in enumerate(ranked_list):
                        if hash(c.page_content) == content_hash:
                            score += 1.0 / (k + rank)
                            break
                except:
                    pass

            rrf_scores[content_hash] = score
            chunk.metadata['rrf_score'] = score

        # Ordenar por RRF score
        sorted_chunks = sorted(
            unique_chunks.values(),
            key=lambda x: x.metadata['rrf_score'],
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

    def query(self, query: str) -> Dict:
        """
        Pipeline completo Fusion RAG.
        """
        start_time = time.time()

        # 1. Query variations
        t1 = time.time()
        variations = self.generate_query_variations(query)
        variation_time = time.time() - t1

        # 2. Multi-strategy retrieval
        t2 = time.time()
        ranked_lists = self.multi_strategy_retrieval(variations)
        retrieval_time = time.time() - t2

        # 3. Fusion (RRF)
        t3 = time.time()
        fused_chunks = self.reciprocal_rank_fusion(ranked_lists)
        fusion_time = time.time() - t3

        # Selecionar top-10 finais
        final_chunks = fused_chunks[:10]

        # 4. Geração
        t4 = time.time()
        response = self.generate(query, final_chunks)
        generation_time = time.time() - t4

        total_latency = time.time() - start_time

        return {
            "response": response,
            "chunks": final_chunks,
            "query_variations": variations,
            "metrics": {
                "latency_total": total_latency,
                "latency_variations": variation_time,
                "latency_retrieval": retrieval_time,
                "latency_fusion": fusion_time,
                "latency_generation": generation_time,
                "num_variations": len(variations),
                "num_strategies": len(ranked_lists),
                "chunks_total": sum(len(rl) for rl in ranked_lists),
                "chunks_unique": len(fused_chunks),
                "chunks_final": len(final_chunks),
                "technique": "fusion"
            }
        }
```

---

## 🎓 Variações Avançadas

### 1. Weighted Fusion
```python
def weighted_fusion(ranked_lists, weights):
    """
    Fusão com pesos por estratégia.

    weights = [0.6, 0.4]  # Semantic 60%, BM25 40%
    """
    for chunk in all_chunks:
        score = 0.0
        for i, ranked_list in enumerate(ranked_lists):
            rank = ranked_list.index(chunk)
            score += weights[i] * (1.0 / (60 + rank))

        chunk.metadata['weighted_score'] = score

    return sorted(chunks, key=lambda x: x.metadata['weighted_score'], reverse=True)
```

---

### 2. Learned Fusion
```python
from sklearn.ensemble import RandomForestClassifier

def learned_fusion(ranked_lists, training_data):
    """
    Aprende weights automaticamente.
    """
    # Features: [semantic_rank, bm25_rank, semantic_score, bm25_score]
    X_train, y_train = prepare_training_data(training_data)

    # Treinar classificador de relevância
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Predizer relevância para cada chunk
    for chunk in all_chunks:
        features = extract_features(chunk, ranked_lists)
        relevance = model.predict_proba([features])[0][1]
        chunk.metadata['learned_score'] = relevance

    return sorted(chunks, key=lambda x: x.metadata['learned_score'], reverse=True)
```

---

### 3. Ensemble com Todas Técnicas
```python
def ultimate_fusion(query):
    """
    Combina TODAS técnicas RAG.
    """
    # Gerar variações
    variations = generate_variations(query)

    # Múltiplas estratégias
    results = []
    for var in variations:
        results.append(baseline_rag(var))
        results.append(hyde_rag(var))
        results.append(semantic_search(var))
        results.append(bm25_search(var))

    # Fusion
    fused = reciprocal_rank_fusion(results)

    # Reranking final
    final = rerank(query, fused[:50], k=10)

    return final
```

**Resultado**: Precision 0.95, Recall 0.95 (mas 10s latência, $0.05/query)

---

## 📚 Referências

**Papers:**
- Cormack et al. (2009) - "Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods"
- Sarto et al. (2023) - "Retrieval-Augmented Generation with Multiple Rankings"

**Implementações:**
- LangChain: `EnsembleRetriever`
- Weaviate: Hybrid search (alpha parameter)

**Benchmarks:**
- BEIR: RRF fusion = +8% nDCG@10 vs best single method
- TREC: Consistent improvements across all datasets

---

## 🎯 Aprendizados Chave

1. **Ensemble > Individual**: Fusion sempre supera técnica individual
2. **RRF é Robusto**: Funciona bem sem tuning, ao contrário de weighted fusion
3. **Query Variations = Recall Booster**: 3-4 variations ideal
4. **Trade-off Extremo**: Melhor qualidade, pior latência/custo
5. **Production Reality**: Ótimo para benchmark, difícil para escala

---

## 📈 Progressão de Complexidade

```
Baseline RAG
    ↓
Fusion (você está aqui) = Meta-técnica
    ↓
    ├─→ Weighted Fusion (tuned)
    ├─→ Learned Fusion (ML)
    └─→ Ultimate Ensemble (ALL techniques)
```

---

**Técnica Anterior**: [Sub-Query](./SUBQUERY.md)
**Próxima Técnica**: [Graph RAG](./GRAPH_RAG.md)
