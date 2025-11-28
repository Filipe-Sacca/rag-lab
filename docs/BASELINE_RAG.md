# Baseline RAG - RAG Tradicional

## 📋 Definição

**Baseline RAG** é a implementação mais simples e direta de Retrieval-Augmented Generation. Representa o padrão "vanilla" sem otimizações avançadas.

É o ponto de partida fundamental para comparar todas as outras técnicas.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. INDEXAÇÃO (Setup - executa 1 vez)
   ├─ Carregar documentos (PDFs, TXTs, etc)
   ├─ Dividir em chunks (512-1024 tokens)
   ├─ Gerar embeddings (text-embedding-004)
   └─ Armazenar no Pinecone

2. RECUPERAÇÃO (Runtime - cada query)
   ├─ User pergunta: "Qual o lucro Q3?"
   ├─ Gerar embedding da pergunta
   ├─ Busca de similaridade no Pinecone
   └─ Retornar top-k chunks (k=5)

3. GERAÇÃO (Runtime)
   ├─ Montar prompt: [System] + [Chunks] + [Query]
   ├─ Enviar para LLM (Gemini 2.5 Flash)
   └─ Retornar resposta final
```

### Exemplo Prático

**Input:**
```
Query: "Qual foi o lucro do terceiro trimestre?"
```

**Processo:**
```python
# 1. Embedding da query
query_vector = embeddings.embed_query("Qual foi o lucro do terceiro trimestre?")
# → [0.023, -0.145, 0.891, ...] (768 dimensões)

# 2. Busca vetorial
results = pinecone.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)
# → Retorna 5 chunks mais similares

# 3. Construir prompt
prompt = f"""
Contexto:
{chunk_1.text}
{chunk_2.text}
{chunk_3.text}
{chunk_4.text}
{chunk_5.text}

Pergunta: {query}

Responda baseado APENAS no contexto acima.
"""

# 4. Gerar resposta
response = llm.invoke(prompt)
```

**Output:**
```
"O lucro líquido do terceiro trimestre foi de R$ 3 bilhões,
representando um crescimento de 15% em relação ao Q2."
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Chunk Size** | 512 tokens | Balance entre contexto e granularidade |
| **Chunk Overlap** | 50 tokens | Evita perder contexto nas bordas |
| **Top-K** | 5 chunks | Suficiente para maioria das perguntas |
| **Embedding Model** | text-embedding-004 | Google - gratuito e eficiente |
| **LLM** | Gemini 1.5 Flash | Custo-benefício ideal |
| **Temperature** | 0.0 | Respostas determinísticas |

---

## ✅ Vantagens

### 1. Simplicidade
- **Implementação**: 50-100 linhas de código
- **Manutenção**: Arquitetura linear, fácil debug
- **Onboarding**: Equipe entende rapidamente

### 2. Velocidade
- **Latência**: ~1-2 segundos total
- **Single retrieval step**: Sem múltiplas chamadas ao Vector DB
- **Direto ao ponto**: Sem processamento intermediário

### 3. Custo-Efetivo
- **Embeddings**: 1 geração por query
- **LLM**: 1 chamada única
- **Vector DB**: 1 busca simples
- **Estimativa**: $0.001-0.003 por query

### 4. Previsibilidade
- **Comportamento**: Determinístico (temp=0)
- **Debugging**: Fácil rastrear erros
- **Métricas**: Baseline estável para comparação

### 5. Suficiente para Casos Simples
- **FAQs**: Perguntas diretas e objetivas
- **Lookup**: "Qual o telefone?", "Quem é o CEO?"
- **Documentação**: Busca em manuais técnicos

---

## ❌ Desvantagens

### 1. Queries Ambíguas
**Problema**: Embedding da query pode não capturar intenção real

```
Query: "Como melhorar performance?"
→ Pode recuperar chunks sobre:
  - Performance de vendas
  - Performance técnica (código)
  - Performance financeira

❌ Sem contexto, não sabe qual o usuário quer
```

**Impacto**: Context Precision baixo (~0.6-0.7)

---

### 2. Queries Complexas Multi-Hop
**Problema**: Precisa de informação de múltiplos documentos correlacionados

```
Query: "Compare lucro Q3 com investimento em marketing"
→ Precisa:
  - Chunk sobre lucro (doc_financeiro.pdf)
  - Chunk sobre marketing (doc_marketing.pdf)

❌ Busca vetorial pode não pegar ambos no top-5
```

**Impacto**: Context Recall baixo (~0.5-0.6)

---

### 3. Vocabulário Mismatch
**Problema**: User usa termos diferentes dos documentos

```
Query: "Quanto a empresa faturou?"
Documento usa: "Receita líquida foi..."

❌ "faturou" ≠ "receita" semanticamente similar, mas pode não ranquear bem
```

**Solução Avançada**: HyDE, Query Expansion

---

### 4. Chunks Grandes = Ruído
**Problema**: Chunks de 512 tokens têm muito contexto extra

```
Chunk recuperado:
"...falamos sobre estratégia de RH, benefícios, treinamento...
[INFORMAÇÃO ÚTIL: lucro foi R$ 3bi]
...depois discutimos plano de carreira, retenção..."

❌ LLM pode se distrair com 80% de ruído
```

**Impacto**: Faithfulness pode cair para 0.7

---

### 5. Sem Reranking
**Problema**: Ordem dos chunks é puramente por similaridade vetorial

```
Top-5 chunks:
1. Score 0.89 → "Lucro preliminar estimado..."  (não final)
2. Score 0.87 → "Discussão sobre lucro..."      (vago)
3. Score 0.85 → "Lucro Q3: R$ 3 bilhões"        (✅ MELHOR)
4. Score 0.82 → Irrelevante
5. Score 0.80 → Irrelevante

❌ Melhor chunk está em 3º lugar
```

**Solução Avançada**: Reranking com Cross-Encoder

---

### 6. Cold Start Problem
**Problema**: Primeira query sempre é lenta

```
1ª query: 3-4 segundos (carregar modelo, conectar Pinecone)
2ª+ query: 1-2 segundos (cache ativo)
```

---

## 📊 Métricas Esperadas (Baseline)

### RAGAS Scores Típicos

| Métrica | Score Esperado | Interpretação |
|---------|----------------|---------------|
| **Faithfulness** | 0.75 - 0.85 | Boa fidelidade aos chunks |
| **Answer Relevancy** | 0.70 - 0.85 | Responde a pergunta, mas pode ser genérico |
| **Context Precision** | 0.60 - 0.75 | ~60% dos chunks são úteis |
| **Context Recall** | 0.50 - 0.70 | Perde 30-50% de info necessária |

### Performance

| Métrica | Valor Típico |
|---------|--------------|
| **Latência** | 1.2 - 2.5s |
| **Custo/Query** | $0.001 - $0.003 |
| **Throughput** | ~30-50 queries/min |

---

## 🎯 Quando Usar Baseline RAG

### ✅ Casos Ideais

**1. FAQs e Documentação Simples**
```
- "Qual o horário de atendimento?"
- "Como resetar senha?"
- "Política de devolução"
```

**2. Lookup Direto**
```
- "Quem é o CFO?"
- "Endereço da matriz"
- "Código do produto X"
```

**3. MVP e Prototipagem**
```
- Validar viabilidade de RAG
- Demonstração rápida
- Baseline para comparação
```

**4. Baixo Volume de Queries**
```
- <100 queries/dia
- Sem SLA crítico
- Budget limitado
```

---

### ❌ Quando NÃO Usar

**1. Queries Analíticas Complexas**
```
❌ "Analise a correlação entre investimento em P&D e crescimento de receita nos últimos 3 anos"
→ Use: Sub-Query ou Graph RAG
```

**2. Domínios com Jargão Técnico**
```
❌ Medicina, Jurídico (vocabulário muito específico)
→ Use: HyDE ou Domain-Specific Embeddings
```

**3. Necessidade de Alta Precisão**
```
❌ Compliance, Regulatório, Financeiro
→ Use: Reranking + Validation
```

**4. Multi-Idioma**
```
❌ Queries em PT, docs em EN
→ Use: Multilingual Embeddings + Query Translation
```

---

## 🔬 Experimentos Recomendados

### 1. Variação de Top-K
```python
# Testar: k=3, k=5, k=10, k=20
# Medir: Context Recall vs Precision
# Hipótese: k maior = recall↑ mas precision↓
```

### 2. Chunk Size Optimization
```python
# Testar: 256, 512, 1024, 2048 tokens
# Medir: Faithfulness e latência
# Hipótese: Chunks menores = mais precisos mas recall menor
```

### 3. Overlap Impact
```python
# Testar: 0%, 10%, 25%, 50% overlap
# Medir: Context Recall
# Hipótese: Overlap evita perder informação nas bordas
```

---

## 💻 Estrutura de Código

```python
# baseline_rag.py

class BaselineRAG:
    """
    Implementação RAG tradicional sem otimizações.

    Pipeline:
    1. Embed query
    2. Similarity search (top-k)
    3. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm):
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm
        self.k = 5  # top-k chunks

    def retrieve(self, query: str) -> List[Document]:
        """Busca vetorial simples"""
        query_vector = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_vector,
            top_k=self.k,
            include_metadata=True
        )
        return self._parse_results(results)

    def generate(self, query: str, context: List[Document]) -> str:
        """Geração com LLM"""
        prompt = self._build_prompt(query, context)
        response = self.llm.invoke(prompt)
        return response.content

    def query(self, query: str) -> Dict:
        """Pipeline completo com métricas"""
        start_time = time.time()

        # Retrieve
        chunks = self.retrieve(query)

        # Generate
        response = self.generate(query, chunks)

        latency = time.time() - start_time

        return {
            "response": response,
            "chunks": chunks,
            "metrics": {
                "latency": latency,
                "chunks_used": len(chunks),
                "technique": "baseline"
            }
        }
```

---

## 📚 Referências

**Papers:**
- Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- Original RAG paper from Meta AI

**Benchmarks:**
- Natural Questions (NQ)
- TriviaQA
- RAGAS evaluation framework

---

## 🎓 Aprendizados Chave

1. **Baseline ≠ Inferior**: Para 60-70% dos casos, é suficiente
2. **Simplicidade tem valor**: Menos pontos de falha, mais fácil debug
3. **Foundation para otimização**: Impossível melhorar sem baseline para comparar
4. **Trade-offs claros**: Velocidade/custo vs precisão/completude

---

## 📈 Roadmap de Melhorias

```
Baseline RAG (você está aqui)
    ↓
    ├─→ HyDE (melhora ambiguidade)
    ├─→ Reranking (melhora precision)
    ├─→ Sub-Query (melhora recall)
    ├─→ Fusion (combina múltiplas estratégias)
    └─→ Graph RAG (queries multi-hop)
```

---

**Próxima Técnica**: [HyDE - Hypothetical Document Embeddings](./HYDE.md)
