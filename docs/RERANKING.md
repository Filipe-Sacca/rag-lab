# Reranking - Refinamento de Resultados com Cross-Encoder

## 📋 Definição

**Reranking** é uma técnica de **pós-processamento** que reordena os chunks recuperados usando um modelo mais sofisticado de relevância.

Funciona em **duas fases**:
1. **Retrieval rápido** (bi-encoder): Busca inicial com muitos candidatos (top-50)
2. **Reranking preciso** (cross-encoder): Reordena para selecionar os melhores (top-5)

**Insight**: Bi-encoders são rápidos mas imprecisos. Cross-encoders são lentos mas muito precisos.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. RETRIEVAL INICIAL (Fase Rápida)
   ├─ Query: "Qual o lucro Q3?"
   ├─ Embedding com bi-encoder (text-embedding-004)
   ├─ Busca de similaridade no Pinecone
   └─ Retornar top-k_initial (k=50) chunks

2. RERANKING (Fase Precisa) ⭐ NOVO
   ├─ Para cada chunk dos 50:
   │  ├─ Concatenar [Query + Chunk]
   │  ├─ Cross-encoder calcula score de relevância
   │  └─ Score: 0.0 (irrelevante) - 1.0 (perfeito)
   ├─ Reordenar chunks por score
   └─ Selecionar top-k_final (k=5) melhores

3. GERAÇÃO
   ├─ Montar prompt com top-5 reranqueados
   ├─ LLM gera resposta
   └─ Retornar resposta final
```

### Comparação Visual

**Baseline RAG:**
```
Query → Embed → Busca top-5 → LLM
                     ↓
               [Pode ter ruído]
```

**Reranking:**
```
Query → Embed → Busca top-50 → Rerank → Top-5 limpo → LLM
                                 ↓
                         [Filtra ruído]
```

---

## 🧠 Bi-Encoder vs Cross-Encoder

### Bi-Encoder (Retrieval)

**Como funciona:**
```python
# Processa separadamente
query_vector = encode(query)        # [0.12, -0.45, ...]
doc_vector = encode(document)       # [0.18, -0.32, ...]

# Compara vetores
similarity = cosine(query_vector, doc_vector)
```

**Características:**
- ✅ **Rápido**: Documentos já estão pré-embedados
- ✅ **Escalável**: Milhões de docs em <100ms
- ❌ **Impreciso**: Não vê query + doc juntos

---

### Cross-Encoder (Reranking)

**Como funciona:**
```python
# Processa JUNTOS
input = "[CLS] query [SEP] document [SEP]"
relevance_score = cross_encoder(input)  # 0.0 - 1.0
```

**Características:**
- ✅ **Muito Preciso**: Vê interação query ↔ doc
- ✅ **Captura Nuances**: Entende contexto completo
- ❌ **Lento**: Precisa processar cada par
- ❌ **Não Escalável**: Impossível para milhões de docs

---

## 💡 Por Que Funciona?

### Problema do Bi-Encoder

```python
Query: "Qual empresa teve maior lucro?"

# Bi-encoder (embeddings independentes):
Doc A: "Amazon teve receita de $500B"
  → query_vec · doc_a_vec = 0.82 (alta similaridade por "empresa", "$")

Doc B: "O lucro da Apple foi $100B, maior que Microsoft $80B"
  → query_vec · doc_b_vec = 0.79 (menor, mas É A RESPOSTA!)

# ❌ Ranqueamento errado: A antes de B
```

### Solução Cross-Encoder

```python
# Cross-encoder vê query + doc juntos:

Input A: "Qual empresa teve maior lucro? [SEP] Amazon teve receita $500B"
  → Score: 0.45 (receita ≠ lucro)

Input B: "Qual empresa teve maior lucro? [SEP] Lucro Apple $100B > Microsoft $80B"
  → Score: 0.95 (responde EXATAMENTE a pergunta)

# ✅ Ranqueamento correto: B antes de A
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Eliminar Ruído

**Query:**
```
"Política de trabalho remoto da empresa"
```

**Retrieval Inicial (top-50):**
```python
# Bi-encoder retorna (misturado):
1. "Política remoto: 3 dias/semana..."           Score: 0.89 ✅
2. "Remote desktop para acesso VPN..."           Score: 0.87 ❌ (tech, não RH)
3. "Trabalho em equipe remota distribuída..."    Score: 0.85 ❌ (conceito, não política)
4. "Benefícios: plano saúde, remoto..."          Score: 0.84 ✅
5. "Política de férias e afastamentos..."        Score: 0.82 ❌
...
48. "Trabalho remoto permitido com aprovação..." Score: 0.61 ✅ (RELEVANTE mas baixo!)
```

**Reranking (Cross-Encoder):**
```python
# Avalia query + cada chunk:
1. "Política remoto: 3 dias/semana..."           Score: 0.96 ✅
48. "Trabalho remoto permitido com aprovação..." Score: 0.91 ✅ (SUBIU!)
4. "Benefícios: plano saúde, remoto..."          Score: 0.78 ✅
2. "Remote desktop para acesso VPN..."           Score: 0.12 ❌ (FILTRADO!)
3. "Trabalho em equipe remota distribuída..."    Score: 0.34 ❌ (FILTRADO!)

# Top-5 final: TODOS relevantes
```

**Resultado**: Context Precision de 0.60 → 0.95

---

### Caso 2: Capturar Negação

**Query:**
```
"Produtos que NÃO contêm glúten"
```

**Bi-Encoder (Falha):**
```python
# Embeddings não capturam "NÃO"
Doc A: "Produto X contém glúten"          Score: 0.88 ❌
Doc B: "Produto Y é livre de glúten"      Score: 0.85 ✅

# ❌ Ranqueia doc ERRADO em 1º
```

**Cross-Encoder (Sucesso):**
```python
Input A: "NÃO contêm glúten [SEP] Produto X contém glúten"
  → Score: 0.05 ❌ (detecta contradição!)

Input B: "NÃO contêm glúten [SEP] Produto Y livre de glúten"
  → Score: 0.98 ✅ (match perfeito)

# ✅ Ranqueia corretamente
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Initial Top-K** | 50 | Suficiente para recall, não sobrecarrega reranker |
| **Final Top-K** | 5 | Mesma quantidade do baseline para LLM |
| **Reranker Model** | ms-marco-MiniLM-L6 | Balance velocidade/precisão |
| **Batch Size** | 32 | Processa chunks em paralelo |
| **Score Threshold** | 0.3 | Descarta chunks muito irrelevantes |

### Modelos de Reranking

| Modelo | Parâmetros | Latência | Precisão | Uso |
|--------|------------|----------|----------|-----|
| **MiniLM-L6** | 22M | ~50ms | ⭐⭐⭐ | Produção (recomendado) |
| **BERT-base** | 110M | ~200ms | ⭐⭐⭐⭐ | Alta precisão |
| **Cohere Rerank** | API | ~100ms | ⭐⭐⭐⭐⭐ | Melhor (pago) |

---

## ✅ Vantagens

### 1. Precisão Massiva
```
Context Precision: 0.60 → 0.90-0.95 (+50%)
Elimina ~80% do ruído do retrieval inicial
```

### 2. Recall Melhorado
```
Buscar top-50 inicial captura chunks "escondidos"
Reranking traz os melhores para top-5
Recall: 0.65 → 0.85 (+30%)
```

### 3. Captura Nuances Semânticas
```
✅ Negações: "não contém"
✅ Comparações: "maior que", "melhor"
✅ Condicionais: "se... então"
✅ Contexto: Entende relação query ↔ doc
```

### 4. Independente da Query
```
Funciona para:
- Queries simples
- Queries complexas
- Qualquer domínio
→ Melhoria consistente
```

### 5. Combina com Outras Técnicas
```
HyDE + Reranking: Precisão máxima
Sub-Query + Reranking: Recall + Precision
Fusion + Reranking: Melhor de todos mundos
```

---

## ❌ Desvantagens

### 1. Latência Adicional
```
Baseline: 1.2s
Reranking: 1.8-2.5s (+0.6-1.3s)

Breakdown:
- Retrieval top-50: 0.1s
- Reranking 50 chunks: +0.5-1.0s (gargalo!)
- LLM: 1.0s
```

### 2. Custo Computacional
```
# Bi-encoder (retrieval):
- 1 embedding da query
- 1 busca vetorial

# Cross-encoder (reranking):
- 50 inferências do modelo
- GPU recomendada (senão +2-3s)

Custo compute: +40-60%
```

### 3. Dependência de Modelo Externo
```
Opções:
1. Self-hosted: Precisa GPU/CPU potente
2. API (Cohere): $1/1K requests (caro em escala)

Complexidade operacional aumenta
```

### 4. Overhead para Queries Simples
```
Query: "Qual o telefone?"
Baseline: 5 chunks, 4 corretos → Precision 0.8

❌ Reranking: +0.8s para ganhar apenas 0.2 precision
→ Não vale o trade-off
```

### 5. Limite de Contexto do Reranker
```
Cross-encoder típico: Max 512 tokens

Chunk grande (1024 tokens):
❌ Precisa truncar → Perde informação
```

### 6. Não Resolve Retrieval Ruim
```
Se retrieval inicial (top-50) não capturou chunk relevante:
❌ Reranking não cria chunk do nada

"Garbage in, garbage out"
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline | Reranking | Δ |
|---------|----------|-----------|---|
| **Faithfulness** | 0.75-0.85 | 0.85-0.92 | +10-15% |
| **Answer Relevancy** | 0.70-0.85 | 0.85-0.95 | +15-20% |
| **Context Precision** | 0.60-0.75 | 0.85-0.95 | +35-50% ⭐ |
| **Context Recall** | 0.50-0.70 | 0.70-0.90 | +30-40% ⭐ |

### Performance

| Métrica | Baseline | Reranking |
|---------|----------|-----------|
| **Latência** | 1.2-2.5s | 1.8-3.5s |
| **Custo/Query** | $0.001-0.003 | $0.002-0.005 |
| **GPU Utilization** | 0% | 20-40% (self-hosted) |
| **Throughput** | ~40 q/min | ~25 q/min |

---

## 🎯 Quando Usar Reranking

### ✅ Casos Ideais

**1. Retrieval com Muito Ruído**
```
✅ Vector DB grande (>100K docs)
✅ Documentos similares entre si
✅ Queries genéricas ("melhorar performance")
```

**2. Alta Precisão Crítica**
```
✅ Legal/Compliance (erro = risco)
✅ Médico/Saúde (precisão = segurança)
✅ Financeiro/Auditoria
```

**3. Queries Complexas**
```
✅ Comparações: "Produto A vs B"
✅ Negações: "Não contém X"
✅ Condicionais: "Se isso, então..."
```

**4. Melhorar Recall + Precision**
```
✅ Buscar top-50 (recall)
✅ Reranquear para top-5 (precision)
→ Melhor dos dois mundos
```

**5. Combinar com Outras Técnicas**
```
✅ HyDE (melhora retrieval) + Reranking (limpa ruído)
✅ Sub-Query (aumenta recall) + Reranking (filtra)
```

---

### ❌ Quando NÃO Usar

**1. Queries Simples e Diretas**
```
❌ "Qual o email?"
❌ "Preço do produto X"
→ Baseline já tem precision alta
```

**2. Vector DB Pequeno e Limpo**
```
❌ <1K documentos bem curados
❌ Retrieval já retorna chunks ótimos
→ Overhead desnecessário
```

**3. Latência Crítica (<1s)**
```
❌ Chatbot em tempo real
❌ Autocompletar em busca
→ +0.8s degrada UX
```

**4. Budget Computacional Limitado**
```
❌ Sem GPU disponível
❌ CPU lenta (reranking leva 2-3s)
→ Inviável
```

**5. Alto Volume de Queries**
```
❌ >100K queries/dia
❌ Custo de reranking API = $100+/dia
→ Não escala financeiramente
```

---

## 🔬 Experimentos Recomendados

### 1. Initial Top-K Optimization
```python
# Testar: k=20, k=50, k=100, k=200
# Medir: Recall vs Latência
# Hipótese: k=50 é sweet spot (95% recall, latência OK)
```

### 2. Reranker Model Comparison
```python
# Testar:
# - MiniLM-L6 (rápido)
# - BERT-base (médio)
# - Cohere API (melhor)
# Medir: Precision vs Latência vs Custo
```

### 3. Score Threshold Impact
```python
# Após reranking, filtrar chunks com score < threshold
# Testar: 0.0, 0.3, 0.5, 0.7
# Medir: Precision (pode subir ao eliminar ruído extremo)
```

### 4. Batch Size Tuning
```python
# Reranker processa chunks em batches
# Testar: batch_size = 8, 16, 32, 64
# Medir: Throughput (GPU utilization)
```

---

## 💻 Estrutura de Código

```python
# reranking.py

from sentence_transformers import CrossEncoder

class RerankingRAG:
    """
    RAG com reranking usando cross-encoder.

    Pipeline:
    1. Retrieval inicial (top-k_initial)
    2. Cross-encoder reranking
    3. Seleção top-k_final
    4. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm, reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm

        # Cross-encoder para reranking
        self.reranker = CrossEncoder(reranker_model)

        self.k_initial = 50  # Retrieval inicial
        self.k_final = 5     # Após reranking

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieval inicial com muitos candidatos.
        """
        query_vector = self.embeddings.embed_query(query)

        # Buscar top-50
        results = self.index.query(
            vector=query_vector,
            top_k=self.k_initial,
            include_metadata=True
        )

        candidates = self._parse_results(results)
        return candidates

    def rerank(self, query: str, candidates: List[Document]) -> List[Document]:
        """
        Reranquear usando cross-encoder.
        """
        # Preparar pares [query, doc]
        pairs = [[query, doc.page_content] for doc in candidates]

        # Cross-encoder calcula scores
        scores = self.reranker.predict(pairs)

        # Adicionar scores aos documentos
        for doc, score in zip(candidates, scores):
            doc.metadata['rerank_score'] = float(score)

        # Reordenar por score
        reranked = sorted(
            candidates,
            key=lambda x: x.metadata['rerank_score'],
            reverse=True
        )

        # Retornar top-k final
        return reranked[:self.k_final]

    def generate(self, query: str, context: List[Document]) -> str:
        """
        Geração com LLM.
        """
        prompt = self._build_prompt(query, context)
        response = self.llm.invoke(prompt, temperature=0.0)
        return response.content

    def query(self, query: str) -> Dict:
        """
        Pipeline completo com métricas.
        """
        start_time = time.time()

        # 1. Retrieval inicial
        t1 = time.time()
        candidates = self.retrieve(query)
        retrieval_time = time.time() - t1

        # 2. Reranking
        t2 = time.time()
        chunks = self.rerank(query, candidates)
        rerank_time = time.time() - t2

        # 3. Generation
        t3 = time.time()
        response = self.generate(query, chunks)
        generation_time = time.time() - t3

        total_latency = time.time() - start_time

        return {
            "response": response,
            "chunks": chunks,
            "metrics": {
                "latency_total": total_latency,
                "latency_retrieval": retrieval_time,
                "latency_rerank": rerank_time,
                "latency_generation": generation_time,
                "chunks_initial": len(candidates),
                "chunks_final": len(chunks),
                "technique": "reranking",
                "avg_rerank_score": sum(c.metadata['rerank_score'] for c in chunks) / len(chunks)
            }
        }
```

---

## 🎓 Variações Avançadas

### 1. Cohere Rerank API
```python
import cohere

co = cohere.Client(api_key="...")

def rerank_with_cohere(query, docs):
    """
    Reranking com API Cohere (melhor precisão).
    """
    results = co.rerank(
        query=query,
        documents=[d.page_content for d in docs],
        top_n=5,
        model="rerank-english-v2.0"
    )

    # Reordenar docs originais
    reranked = [docs[r.index] for r in results]
    return reranked
```

**Vantagens**: Melhor modelo, sem GPU local
**Desvantagens**: $1/1K requests

---

### 2. Hybrid Reranking
```python
def hybrid_rerank(query, docs):
    """
    Combina cross-encoder + BM25 lexical.
    """
    # Cross-encoder (semântico)
    semantic_scores = cross_encoder.predict([[query, d] for d in docs])

    # BM25 (lexical keyword matching)
    lexical_scores = bm25.get_scores(query, docs)

    # Combinar (weighted average)
    final_scores = 0.7 * semantic_scores + 0.3 * lexical_scores

    # Reordenar
    return sorted(zip(docs, final_scores), key=lambda x: x[1], reverse=True)
```

**Benefício**: Captura keyword + semântica

---

### 3. Two-Stage Reranking
```python
def two_stage_rerank(query, docs):
    """
    1º estágio: MiniLM rápido (top-50 → top-20)
    2º estágio: BERT preciso (top-20 → top-5)
    """
    # Stage 1: Rápido
    stage1 = minilm_reranker.predict(query, docs, k=20)

    # Stage 2: Preciso
    stage2 = bert_reranker.predict(query, stage1, k=5)

    return stage2
```

**Benefício**: Balance latência/precisão

---

## 📚 Referências

**Papers:**
- Nogueira et al. (2019) - "Document Ranking with Cross-Encoders"
- Pradeep et al. (2021) - "Dense vs. Sparse Retrieval for Question Answering"

**Modelos:**
- Sentence-Transformers: `cross-encoder/ms-marco-*`
- Cohere Rerank: API comercial
- OpenAI Embedding: Não tem reranker nativo

**Benchmarks:**
- MS MARCO: +15% MRR@10 vs bi-encoder alone
- BEIR: +12% nDCG@10

---

## 🎯 Aprendizados Chave

1. **Duas Fases Essenciais**: Retrieval rápido + Reranking preciso
2. **Trade-off Latência/Precisão**: +0.8s para +50% precision (geralmente vale)
3. **Cross-Encoder ≠ Bi-Encoder**: Modelos diferentes, propósitos diferentes
4. **Top-50 Initial**: Sweet spot entre recall e latência de reranking
5. **Combina com Tudo**: Funciona com HyDE, Sub-Query, Fusion

---

## 📈 Progressão de Complexidade

```
Baseline RAG
    ↓
Reranking (você está aqui)
    ↓
    ├─→ Hybrid Reranking (semântico + lexical)
    ├─→ Two-Stage (fast → precise)
    └─→ HyDE + Reranking (combo poderoso)
```

---

**Técnica Anterior**: [HyDE](./HYDE.md)
**Próxima Técnica**: [Sub-Query Decomposition](./SUBQUERY.md)
