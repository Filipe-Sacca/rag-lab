# Parent Document Retrieval - Precisão na Busca, Contexto na Resposta

## 📋 Definição

**Parent Document Retrieval** resolve o **dilema do tamanho de chunk**: buscar com chunks pequenos (alta precisão) mas retornar documentos completos (contexto rico).

A técnica mantém **dois índices**:
1. **Índice de busca**: Mini-chunks (128-256 tokens) - embeddings precisos
2. **Índice de contexto**: Documentos pais completos - informação completa

**Insight**: Tamanho ótimo para busca ≠ Tamanho ótimo para geração.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. INDEXAÇÃO (Setup - Dois Níveis)
   ├─ Documento original: "financial_report_q3.pdf"
   │
   ├─ Criar mini-chunks (128 tokens):
   │  ├─ Child 1: "Lucro Q3 foi R$ 3bi..."
   │  ├─ Child 2: "Margem operacional 15%..."
   │  ├─ Child 3: "Investimento P&D R$ 500mi..."
   │  └─ [Total: 20 mini-chunks]
   │
   ├─ Armazenar mini-chunks no Vector DB
   │  └─ Com metadata: {parent_id: "doc_123"}
   │
   └─ Armazenar documento pai separadamente
      └─ Document Store: {id: "doc_123", content: [...]}

2. RETRIEVAL (Runtime)
   ├─ Query: "Qual o lucro Q3?"
   ├─ Buscar nos MINI-CHUNKS (precisão)
   │  └─ Match: Child 1 (score: 0.95)
   └─ Retornar DOCUMENTO PAI completo
      └─ Lookup: parent_id → doc_123 (contexto)

3. GERAÇÃO
   ├─ Prompt com documento PAI (não mini-chunk)
   ├─ LLM tem contexto completo
   └─ Resposta rica e detalhada
```

### Comparação Visual

**Baseline RAG (chunks médios 512 tokens):**
```
Documento → Chunks 512 tokens → Embed → Busca → Retorna chunks 512
                ↓
     Precisão OK, Contexto OK (compromise)
```

**Parent Document:**
```
Documento → Split em duas camadas:
  ├─ Mini-chunks 128 tokens → Embed → Busca (PRECISÃO)
  └─ Documento completo → Store → Retorna (CONTEXTO)
                                    ↓
                          Melhor dos dois mundos
```

---

## 💡 Por Que Funciona?

### Problema: Chunk Size Dilemma

**Chunks Pequenos (128 tokens):**
```
✅ Embedding mais preciso (conceito único)
✅ Match de similaridade mais exato
✅ Menos ruído
❌ Contexto insuficiente para LLM
❌ Pode perder informação adjacente
```

**Chunks Grandes (1024 tokens):**
```
✅ Contexto rico
✅ Informação completa
❌ Embedding genérico (múltiplos conceitos)
❌ Match de similaridade impreciso
❌ Muito ruído
```

**Parent Document = Best of Both:**
```
Busca com 128 tokens (precisão)
  ↓
Encontra chunk exato: "Lucro Q3: R$ 3bi"
  ↓
Retorna documento completo que CONTÉM esse chunk
  ↓
LLM vê: Contexto de todo relatório Q3
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query Específica com Necessidade de Contexto

**Documento Original** (2000 tokens):
```
RELATÓRIO FINANCEIRO Q3 2024

Resumo Executivo:
A empresa teve desempenho excepcional no terceiro trimestre...

Resultados Financeiros:
Lucro líquido: R$ 3 bilhões
Crescimento YoY: 15%
Margem operacional: 18%

Análise por Segmento:
- Cloud: R$ 1.5bi (50% do lucro)
- Hardware: R$ 1.0bi (33%)
- Serviços: R$ 500mi (17%)

Investimentos:
P&D: R$ 800mi (+20% vs Q2)
Marketing: R$ 200mi

Projeções Q4:
Esperamos manter crescimento...
```

**Indexação:**
```python
# Mini-chunks (128 tokens cada):
chunk_1 = "Lucro líquido: R$ 3 bilhões. Crescimento YoY: 15%"
chunk_2 = "Margem operacional: 18%"
chunk_3 = "Cloud: R$ 1.5bi (50% do lucro)"
chunk_4 = "P&D: R$ 800mi (+20% vs Q2)"
# ... etc

# Cada chunk tem metadata:
metadata = {
    "parent_id": "financial_q3_2024",
    "chunk_index": 1,
    "source": "financial_report_q3.pdf"
}
```

**Query:**
```
"Qual foi o lucro do Q3 e como ele se distribui por segmento?"
```

**Baseline RAG (chunk 512 tokens):**
```python
# Busca retorna chunk médio:
chunk_retrieved = """
Resultados Financeiros:
Lucro líquido: R$ 3 bilhões
Crescimento YoY: 15%
Margem operacional: 18%
... [mais 300 tokens de contexto genérico]
"""

# ❌ Chunk TEM o lucro, mas NÃO tem distribuição por segmento
# ❌ LLM responde: "Lucro R$ 3bi, mas não tenho info sobre segmentos"
```

**Parent Document:**
```python
# Busca encontra mini-chunk preciso:
mini_chunk = "Lucro líquido: R$ 3 bilhões. Crescimento YoY: 15%"

# Retorna documento PAI completo:
parent_doc = """
[RELATÓRIO COMPLETO 2000 tokens]
Inclui: Lucro + Margem + Segmentos + Investimentos + Projeções
"""

# ✅ LLM responde:
# "Lucro Q3: R$ 3bi. Distribuição: Cloud R$ 1.5bi (50%),
#  Hardware R$ 1.0bi (33%), Serviços R$ 500mi (17%)"
```

**Resultado**: Recall completo com precisão na busca.

---

### Caso 2: Evitar Fragmentação de Informação

**Documento: Tutorial Machine Learning** (1500 tokens)

**Baseline (chunks 512):**
```python
# Documento fragmentado em 3 chunks:
chunk_1 = "Introdução ML... tipos de algoritmos..."
chunk_2 = "Exemplo prático: modelo de regressão..."
chunk_3 = "Código Python para treinar modelo..."

# Query: "Como treinar modelo de regressão?"

# Busca retorna chunk_2 (exemplo)
# ❌ Falta chunk_3 (código)
# ❌ Resposta incompleta
```

**Parent Document:**
```python
# Mini-chunks (128 tokens):
mini_1 = "Modelo de regressão linear prediz valores..."
mini_2 = "Exemplo: prever preço casa baseado em features..."
mini_3 = "Código Python: from sklearn..."

# Busca encontra mini_2 (match exato "modelo regressão")

# Retorna documento PAI completo:
# ✅ Inclui: Introdução + Exemplo + Código completo
# ✅ Resposta completa com tudo conectado
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Child Chunk Size** | 128-256 tokens | Balance precisão/granularidade |
| **Parent Type** | Documento completo OU seção | Depende do domínio |
| **Top-K Children** | 3-5 | Múltiplos matches = mais pais |
| **Deduplication** | Sim | Evitar retornar mesmo pai 2x |
| **Max Parent Tokens** | 2048-4096 | Limite do context window |

### Estratégias de Parentesco

| Estratégia | Child | Parent | Uso |
|------------|-------|--------|-----|
| **Document-Level** | Mini-chunk 128 | Doc completo | Docs pequenos (<2K tokens) |
| **Section-Level** | Parágrafo | Seção completa | Docs grandes (>10K tokens) |
| **Sliding Window** | Sentença | Janela ±5 sentenças | Máxima precisão |

---

## ✅ Vantagens

### 1. Resolve Chunk Size Dilemma
```
Não precisa mais escolher entre:
- Chunks pequenos (precisão) OU
- Chunks grandes (contexto)

Tem AMBOS simultaneamente
```

### 2. Precision Massiva
```
Mini-chunk embedding:
"Lucro Q3: R$ 3bi" → Vector focado

vs Baseline (chunk 512 tokens):
"Resumo executivo... lucro... margem... investimentos..."
→ Vector genérico

Precision: 0.70 → 0.90 (+28%)
```

### 3. Contexto Completo
```
LLM recebe documento inteiro:
→ Pode sintetizar informações de múltiplas partes
→ Resposta mais rica e conectada
→ Reduz "Não tenho essa informação" (recall +30%)
```

### 4. Simples de Implementar
```python
# Apenas 2 passos extras:
1. Split em mini-chunks + armazenar parent_id
2. Lookup de parent após retrieval

Complexidade: Baixa (vs Graph RAG)
```

### 5. Funciona com Qualquer Técnica
```
Parent Document + HyDE = ótimo
Parent Document + Reranking = ótimo
Parent Document + Sub-Query = ótimo

É uma "camada" complementar
```

---

## ❌ Desvantagens

### 1. Contexto Pode Ser Excessivo
```
Query: "Qual o telefone?"

Mini-chunk match: "Telefone: (11) 1234-5678"

Parent retornado: Documento 2000 tokens sobre empresa
→ Inclui: História, missão, valores, contatos...

❌ 1900 tokens irrelevantes para LLM
❌ Custo desnecessário
```

### 2. Deduplicação Necessária
```
Query: "Lucro e margem Q3"

Matches:
- Mini-chunk A: "Lucro R$ 3bi" → Parent: doc_123
- Mini-chunk B: "Margem 18%" → Parent: doc_123

❌ Sem dedup: Retorna doc_123 duas vezes
→ Desperdiça tokens
```

### 3. Limite de Context Window
```
Top-5 mini-chunks de 5 documentos diferentes:
→ 5 parents × 2000 tokens = 10K tokens

Se LLM tem limite 8K:
❌ Não cabe tudo
Solução: Comprimir ou limitar top-k
```

### 4. Parent Pode Ser Muito Grande
```
Parent = PDF de 50 páginas (50K tokens)

❌ Impossível passar para LLM
Solução: Usar Section-Level (não Document-Level)
```

### 5. Indexação Mais Lenta
```
1 documento → 20 mini-chunks
vs Baseline: 1 documento → 4 chunks

Indexação: 5x mais chunks para embedar
Tempo: +80-100%
```

### 6. Custo de Storage Aumenta
```
Baseline:
- Vector DB: 1000 chunks

Parent Document:
- Vector DB: 5000 mini-chunks
- Document Store: 1000 parents

Storage: +400-500%
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline (512 tokens) | Parent Document | Δ |
|---------|----------------------|-----------------|---|
| **Faithfulness** | 0.75-0.85 | 0.85-0.92 | +10-15% |
| **Answer Relevancy** | 0.70-0.85 | 0.82-0.93 | +15-20% |
| **Context Precision** | 0.60-0.75 | 0.80-0.92 | +25-35% ⭐ |
| **Context Recall** | 0.50-0.70 | 0.75-0.90 | +35-50% ⭐ |

### Performance

| Métrica | Baseline | Parent Document |
|---------|----------|-----------------|
| **Latência** | 1.2-2.5s | 1.5-3.0s |
| **Custo/Query** | $0.001-0.003 | $0.002-0.005 |
| **Indexação Time** | 30 min | 50-60 min |
| **Storage** | 1x | 4-5x |

---

## 🎯 Quando Usar Parent Document

### ✅ Casos Ideais

**1. Documentos Estruturados com Seções**
```
✅ Relatórios (financeiros, técnicos)
✅ Artigos acadêmicos (abstract, intro, methods...)
✅ Documentação técnica (seções lógicas)
```

**2. Informação Interconectada**
```
✅ Tutorial completo (passos dependem uns dos outros)
✅ Análises (contexto geral + detalhes específicos)
✅ Casos de uso (setup + implementação + resultados)
```

**3. Queries Específicas com Necessidade de Contexto**
```
✅ "Qual a conclusão do experimento X?"
   → Busca "experimento X", retorna seção completa com métodos + resultados + conclusão
```

**4. Documentos Pequenos-Médios (<5K tokens)**
```
✅ Parent = documento completo cabe no context window
✅ Não precisa comprimir ou truncar
```

**5. Alta Precisão Necessária**
```
✅ Legal, compliance (precisa encontrar cláusula EXATA)
✅ Medicina (sintoma específico → contexto completo)
```

---

### ❌ Quando NÃO Usar

**1. Documentos Muito Grandes**
```
❌ PDFs de 100+ páginas
❌ Parent = 50K tokens (não cabe no LLM)
→ Use Section-Level ou Baseline com chunks médios
```

**2. Informação Fragmentada e Independente**
```
❌ FAQs (cada pergunta independente)
❌ Glossários (definições isoladas)
→ Baseline suficiente
```

**3. Queries que NÃO Precisam de Contexto**
```
❌ "Qual o telefone?" → Só precisa do número
❌ "Preço do produto X?" → Só precisa do valor
→ Parent adiciona ruído desnecessário
```

**4. Budget de Storage Limitado**
```
❌ 5x mais chunks para armazenar
❌ Custo Pinecone aumenta proporcionalmente
```

**5. Latência Crítica**
```
❌ Retornar parent grande = mais tokens para LLM
❌ +30-50% latência vs baseline
```

---

## 🔬 Experimentos Recomendados

### 1. Child Chunk Size Optimization
```python
# Testar: 64, 128, 256, 512 tokens
# Medir: Precision vs Recall
# Hipótese: 128-256 = sweet spot
```

### 2. Parent Granularity
```python
# Testar:
# - Document-level (doc completo)
# - Section-level (por seção)
# - Paragraph-level (parágrafo)
# Medir: Context relevance vs tokens usados
```

### 3. Deduplication Strategy
```python
# Quando múltiplos children → mesmo parent:
# - Retornar parent 1x (dedup)
# - Retornar parent múltiplas vezes (reforço)
# - Merge de múltiplos parents
# Medir: Token efficiency vs recall
```

---

## 💻 Estrutura de Código

```python
# parent_document.py

from typing import List, Dict

class ParentDocumentRAG:
    """
    Parent Document Retrieval: Busca mini-chunks, retorna parents.

    Pipeline:
    1. Retrieval com mini-chunks (precisão)
    2. Lookup de parents (contexto)
    3. Deduplicação
    4. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm, document_store):
        self.index = pinecone_index  # Mini-chunks
        self.embeddings = embeddings
        self.llm = llm
        self.doc_store = document_store  # Parent documents

        self.child_chunk_size = 128
        self.k_children = 10  # Buscar 10 mini-chunks

    def index_document(self, document: str, doc_id: str):
        """
        Indexa documento em dois níveis.
        """
        # 1. Criar mini-chunks
        mini_chunks = self._split_into_mini_chunks(document, self.child_chunk_size)

        # 2. Armazenar parent no document store
        self.doc_store.add({
            "id": doc_id,
            "content": document
        })

        # 3. Embed e armazenar mini-chunks no Vector DB
        for i, chunk in enumerate(mini_chunks):
            chunk_id = f"{doc_id}_child_{i}"
            vector = self.embeddings.embed_query(chunk)

            self.index.upsert([(
                chunk_id,
                vector,
                {
                    "text": chunk,
                    "parent_id": doc_id,  # ⭐ Link para parent
                    "chunk_index": i
                }
            )])

    def retrieve_children(self, query: str) -> List[Dict]:
        """
        Busca mini-chunks (children).
        """
        query_vector = self.embeddings.embed_query(query)

        results = self.index.query(
            vector=query_vector,
            top_k=self.k_children,
            include_metadata=True
        )

        children = []
        for match in results['matches']:
            children.append({
                "text": match['metadata']['text'],
                "parent_id": match['metadata']['parent_id'],
                "score": match['score']
            })

        return children

    def retrieve_parents(self, children: List[Dict]) -> List[str]:
        """
        Recupera documentos parents e deduplica.
        """
        # Coletar parent_ids únicos
        parent_ids = list(set([c['parent_id'] for c in children]))

        # Buscar parents no document store
        parents = []
        for parent_id in parent_ids:
            parent_doc = self.doc_store.get(parent_id)
            if parent_doc:
                parents.append(parent_doc['content'])

        return parents

    def generate(self, query: str, parents: List[str]) -> str:
        """
        Geração com documentos parents completos.
        """
        # Montar contexto com parents
        context = "\n\n---\n\n".join(parents)

        prompt = f"""
Contexto (documentos completos):
{context}

Pergunta: {query}

Responda baseado no contexto acima.
"""

        response = self.llm.invoke(prompt, temperature=0.0)
        return response.content

    def query(self, query: str) -> Dict:
        """
        Pipeline completo Parent Document RAG.
        """
        start_time = time.time()

        # 1. Retrieve mini-chunks
        t1 = time.time()
        children = self.retrieve_children(query)
        children_time = time.time() - t1

        # 2. Retrieve parents
        t2 = time.time()
        parents = self.retrieve_parents(children)
        parents_time = time.time() - t2

        # 3. Generation
        t3 = time.time()
        response = self.generate(query, parents)
        generation_time = time.time() - t3

        total_latency = time.time() - start_time

        # Calcular tokens
        total_tokens = sum(len(p.split()) for p in parents)

        return {
            "response": response,
            "children_matched": children,
            "parents_retrieved": len(parents),
            "metrics": {
                "latency_total": total_latency,
                "latency_children": children_time,
                "latency_parents": parents_time,
                "latency_generation": generation_time,
                "children_count": len(children),
                "parents_count": len(parents),
                "context_tokens": total_tokens,
                "technique": "parent_document"
            }
        }

    def _split_into_mini_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split texto em mini-chunks de tamanho fixo.
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)

        return chunks
```

---

## 🎓 Variações Avançadas

### 1. Section-Level Parents
```python
def index_with_sections(document, sections):
    """
    Parent = seção (não documento completo).
    """
    for section in sections:
        # Mini-chunks dentro da seção
        mini_chunks = split(section.content, 128)

        # Parent = seção
        parent_id = f"{doc_id}_{section.title}"
        doc_store.add(parent_id, section.content)

        # Children linkam para seção
        for chunk in mini_chunks:
            index.add(chunk, parent_id=parent_id)
```

### 2. Sliding Window Parents
```python
def sliding_window_parents(text):
    """
    Child = sentença
    Parent = ±5 sentenças ao redor
    """
    sentences = split_sentences(text)

    for i, sentence in enumerate(sentences):
        # Child = sentença única
        child = sentence

        # Parent = janela ao redor
        start = max(0, i - 5)
        end = min(len(sentences), i + 6)
        parent = " ".join(sentences[start:end])

        index.add(child, parent_content=parent)
```

---

## 📚 Referências

**Papers:**
- LangChain Documentation - "Parent Document Retriever"
- Pinecone - "Advanced RAG: Parent-Child Chunking"

**Implementações:**
- LangChain: `ParentDocumentRetriever`
- LlamaIndex: `DocumentSummaryIndex` (similar)

---

## 🎯 Aprendizados Chave

1. **Chunk Size Dilemma Resolvido**: Precisão (busca) + Contexto (geração)
2. **Simples mas Poderoso**: +30% recall com implementação fácil
3. **Complementar**: Funciona com HyDE, Reranking, Sub-Query
4. **Trade-off Storage**: 5x mais chunks, mas vale a pena
5. **Production-Ready**: Usado amplamente em sistemas reais

---

**Técnica Anterior**: [Graph RAG](./GRAPH_RAG.md)
**Próxima Técnica**: [Agentic RAG](./AGENTIC_RAG.md)
