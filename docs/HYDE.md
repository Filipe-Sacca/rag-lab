# HyDE - Hypothetical Document Embeddings

## 📋 Definição

**HyDE** (Hypothetical Document Embeddings) é uma técnica avançada de otimização de query que **inverte a lógica tradicional do RAG**.

Ao invés de buscar com a pergunta, o LLM **gera uma resposta hipotética** (mesmo que incorreta), e essa resposta é usada para buscar documentos similares.

**Insight**: Respostas são semanticamente mais próximas de documentos do que perguntas.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. GERAÇÃO HIPOTÉTICA (Novo!)
   ├─ User pergunta: "Qual o lucro Q3?"
   ├─ LLM gera resposta hipotética SEM ver documentos
   └─ Hipótese: "O lucro do Q3 foi de aproximadamente R$ 3 bilhões..."

2. EMBEDDING DA HIPÓTESE (Diferente!)
   ├─ Gerar embedding da RESPOSTA (não da pergunta)
   └─ Vector: [0.145, -0.891, 0.234, ...]

3. RECUPERAÇÃO
   ├─ Busca de similaridade no Pinecone
   └─ Retornar top-k chunks

4. GERAÇÃO FINAL
   ├─ Montar prompt: [Chunks] + [Query Original]
   ├─ LLM gera resposta REAL (baseada nos chunks)
   └─ Retornar resposta final
```

### Comparação Visual

**Baseline RAG:**
```
Query: "Qual o lucro?"
  ↓ [Embed]
Vector da PERGUNTA → Busca → Chunks
```

**HyDE:**
```
Query: "Qual o lucro?"
  ↓ [LLM gera]
Hipótese: "O lucro foi R$ 3bi com crescimento..."
  ↓ [Embed]
Vector da RESPOSTA → Busca → Chunks (melhores!)
```

---

## 💡 Por Que Funciona?

### Problema do Baseline

```python
# Embedding da pergunta
query = "Qual foi o lucro?"
query_vector = embed("Qual foi o lucro?")

# Documentos dizem:
doc = "A receita líquida do trimestre atingiu R$ 3 bilhões..."

# ❌ Distância semântica:
# "Qual foi o lucro?" ≠≠ "receita líquida atingiu R$ 3bi"
# (Pergunta vs Declaração = estilos diferentes)
```

### Solução HyDE

```python
# LLM gera hipótese (estilo declarativo)
hypothesis = "O lucro do trimestre foi de aproximadamente R$ 3 bilhões"

# Embed a hipótese
hyp_vector = embed(hypothesis)

# ✅ Agora:
# "lucro foi R$ 3 bilhões" ≈≈ "receita líquida atingiu R$ 3 bilhões"
# (Declaração vs Declaração = semanticamente próximas!)
```

**Resultado**: Similarity score sobe de 0.75 → 0.92

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query Ambígua

**Input:**
```
Query: "Como melhorar performance?"
```

**Baseline RAG:**
```python
# Embedding direto da query
results = search(embed("Como melhorar performance?"))

# Chunks recuperados (confusos):
1. "Performance de vendas aumentou 20%..."      (marketing)
2. "Otimização de código reduz latência..."     (tech)
3. "Performance financeira do Q3..."            (finance)

# ❌ Sem contexto, pega de tudo
```

**HyDE:**
```python
# 1. LLM gera hipótese (assume contexto tech)
hypothesis = llm.generate("""
Pergunta: Como melhorar performance?
Gere uma resposta hipotética técnica:
""")
# → "Para melhorar performance de sistemas, otimize queries SQL,
#    implemente cache Redis, use CDN para assets..."

# 2. Busca com a hipótese
results = search(embed(hypothesis))

# Chunks recuperados (focados):
1. "Otimização de queries SQL: indexação..."    ✅
2. "Implementação de cache Redis..."            ✅
3. "CDN para distribuição de assets..."         ✅

# ✅ Contexto técnico capturado!
```

**Melhoria**: Context Precision de 0.60 → 0.85

---

### Caso 2: Vocabulário Mismatch

**Input:**
```
Query: "Quanto a empresa faturou no último trimestre?"
```

**Baseline:**
```python
# Busca com "faturou"
results = search(embed("faturou no último trimestre"))

# Documentos usam "receita líquida", não "faturou"
# ❌ Similarity baixa (0.68)
```

**HyDE:**
```python
# 1. Hipótese usa vocabulário corporativo
hypothesis = "A receita líquida consolidada do terceiro
              trimestre atingiu R$ 3 bilhões..."

# 2. Busca
results = search(embed(hypothesis))

# ✅ "receita líquida" match perfeito (0.94)
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Hypothesis Prompt** | "Gere resposta detalhada..." | Instruir LLM a ser específico |
| **Hypothesis Length** | 100-200 tokens | Balance entre detalhe e custo |
| **LLM** | Gemini 2.5 Flash | Rápido e barato para hipóteses |
| **Temperature** | 0.7 | Criatividade para preencher lacunas |
| **Top-K** | 5 chunks | Mesmo do baseline |
| **Fallback** | Baseline se hipótese vazia | Segurança |

---

## ✅ Vantagens

### 1. Maior Precisão Semântica
```
Melhoria típica: +15-25% em similarity scores
Context Precision: 0.60 → 0.85
```

### 2. Resolve Vocabulário Mismatch
```
User: "faturamento"
Docs: "receita líquida"
→ Hipótese usa termo correto automaticamente
```

### 3. Captura Intenção Implícita
```
Query vaga: "Como está a empresa?"
Hipótese especifica: "Situação financeira, crescimento, desafios..."
→ Busca mais direcionada
```

### 4. Funciona com Queries Abertas
```
Baseline falha: "Explique machine learning"
HyDE gera: "Machine learning é... utiliza algoritmos... exemplos..."
→ Busca captura material didático
```

### 5. Multi-Idioma Natural
```
Query PT: "Qual o lucro?"
Hipótese PT: "O lucro foi..."
Docs EN: "Profit was..."
→ Embedding multilingual aproxima automaticamente
```

---

## ❌ Desvantagens

### 1. Custo 2x Maior
```
Baseline: 1 chamada LLM (geração final)
HyDE: 2 chamadas LLM (hipótese + geração final)

Custo: $0.002 → $0.004 por query (+100%)
```

### 2. Latência Aumentada
```
Baseline: 1.2s
HyDE: 1.8-2.5s (+50-100%)

Breakdown:
- Geração hipótese: +0.5-0.8s
- Resto: igual
```

### 3. Risco de Viés na Hipótese
```
Query: "Qual a política de RH?"
Hipótese (viés): "Políticas progressivas de diversidade..."

❌ Se docs não falam de diversidade, busca falha
→ Hipótese assumiu contexto errado
```

### 4. Queries Factuais Simples = Overhead Desnecessário
```
Query: "Qual o telefone?"
Baseline: Busca direto, retorna em 1s
HyDE: Gera hipótese desnecessária, +0.8s

❌ Complexidade sem benefício
```

### 5. Dependência de Qualidade do Prompt
```python
# Prompt ruim:
"Responda a pergunta"
→ Hipótese genérica, não ajuda

# Prompt bom:
"Gere resposta técnica detalhada com termos específicos do domínio"
→ Hipótese útil
```

### 6. Não Funciona para Lookup
```
Query: "Email do CEO"
Hipótese: "O email do CEO é ceo@empresa.com"

❌ LLM inventou email (alucinação)
→ Busca com dado falso
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline | HyDE | Δ |
|---------|----------|------|---|
| **Faithfulness** | 0.75-0.85 | 0.80-0.90 | +5-7% |
| **Answer Relevancy** | 0.70-0.85 | 0.85-0.95 | +15-20% |
| **Context Precision** | 0.60-0.75 | 0.75-0.90 | +20-25% |
| **Context Recall** | 0.50-0.70 | 0.55-0.75 | +5-10% |

### Performance

| Métrica | Baseline | HyDE |
|---------|----------|------|
| **Latência** | 1.2-2.5s | 1.8-3.5s |
| **Custo/Query** | $0.001-0.003 | $0.003-0.006 |
| **Throughput** | ~40 q/min | ~25 q/min |

---

## 🎯 Quando Usar HyDE

### ✅ Casos Ideais

**1. Queries Abertas e Exploratórias**
```
✅ "Explique a estratégia de crescimento"
✅ "Como funciona o processo de vendas?"
✅ "Qual a visão da empresa sobre IA?"
```

**2. Vocabulário Técnico Específico**
```
✅ User: "quebrou" → Doc: "falha crítica de sistema"
✅ User: "gastou" → Doc: "despesas operacionais"
```

**3. Queries Ambíguas**
```
✅ "Como melhorar performance?" (tech vs business)
✅ "Status do projeto?" (qual projeto?)
```

**4. Domínios com Jargão**
```
✅ Medicina: sintomas → diagnósticos
✅ Jurídico: questões → artigos de lei
✅ Financeiro: perguntas → relatórios técnicos
```

**5. Conhecimento Implícito**
```
✅ "Regulamentações aplicáveis"
   → Hipótese: "LGPD, SOX, ISO27001..." (contexto BR)
```

---

### ❌ Quando NÃO Usar

**1. Queries Factuais Simples**
```
❌ "Qual o telefone?"
❌ "Endereço da matriz"
❌ "Código do produto X"
→ Use: Baseline (mais rápido)
```

**2. Lookup Direto**
```
❌ "Email do CEO"
❌ "Preço do plano premium"
→ Risco: LLM alucina dados específicos
```

**3. Dados Temporais Precisos**
```
❌ "Preço da ação hoje"
❌ "Lucro exato Q3 2024"
→ Hipótese pode usar data/valor errado
```

**4. Budget Limitado**
```
❌ >10K queries/dia com budget apertado
→ Custo 2x pode ser proibitivo
```

**5. Latência Crítica**
```
❌ Chatbot em tempo real (<1s esperado)
→ +0.8s pode degradar UX
```

---

## 🔬 Experimentos Recomendados

### 1. Hypothesis Length Optimization
```python
# Testar: 50, 100, 200, 500 tokens
# Medir: Context Precision vs Latência
# Hipótese: 100-200 tokens = sweet spot
```

### 2. Temperature Impact
```python
# Testar: 0.0, 0.3, 0.7, 1.0
# Medir: Diversity vs Hallucination
# Hipótese: 0.5-0.7 balanceia criatividade
```

### 3. Multi-Hypothesis Ensemble
```python
# Gerar 3 hipóteses diferentes
# Buscar com cada uma
# Fusão dos resultados (RRF)
# Medir: Recall improvement
```

### 4. Prompt Engineering Impact
```python
# Testar:
# - "Responda objetivamente"
# - "Gere resposta técnica detalhada"
# - "Use termos do domínio {domain}"
# Medir: Precision delta
```

---

## 💻 Estrutura de Código

```python
# hyde.py

class HyDERAG:
    """
    HyDE: Busca com documento hipotético ao invés da query.

    Pipeline:
    1. Gerar resposta hipotética (LLM)
    2. Embed hipótese
    3. Similarity search
    4. LLM generation final
    """

    def __init__(self, pinecone_index, embeddings, llm):
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm
        self.k = 5

    def generate_hypothesis(self, query: str) -> str:
        """
        Gera resposta hipotética detalhada.
        """
        prompt = f"""
Você é um assistente especializado.

Pergunta do usuário: {query}

Gere uma resposta hipotética DETALHADA (100-200 palavras)
usando termos técnicos e específicos do domínio.

NÃO diga "não sei" ou "preciso verificar".
Seja específico e declarativo, mesmo que a resposta seja uma estimativa.

Resposta hipotética:
"""
        response = self.llm.invoke(
            prompt,
            temperature=0.7,  # Criatividade para preencher lacunas
            max_tokens=200
        )
        return response.content

    def retrieve(self, query: str) -> List[Document]:
        """
        Busca usando embedding da HIPÓTESE.
        """
        # Gerar hipótese
        hypothesis = self.generate_hypothesis(query)

        # Embed hipótese (não query original)
        hyp_vector = self.embeddings.embed_query(hypothesis)

        # Busca
        results = self.index.query(
            vector=hyp_vector,
            top_k=self.k,
            include_metadata=True
        )

        return self._parse_results(results), hypothesis

    def generate(self, query: str, context: List[Document]) -> str:
        """
        Geração final com query ORIGINAL (não hipótese).
        """
        prompt = self._build_prompt(query, context)
        response = self.llm.invoke(prompt, temperature=0.0)
        return response.content

    def query(self, query: str) -> Dict:
        """
        Pipeline completo com métricas.
        """
        start_time = time.time()

        # Retrieve com HyDE
        chunks, hypothesis = self.retrieve(query)

        # Generate
        response = self.generate(query, chunks)

        latency = time.time() - start_time

        return {
            "response": response,
            "chunks": chunks,
            "hypothesis": hypothesis,  # Para debug
            "metrics": {
                "latency": latency,
                "chunks_used": len(chunks),
                "technique": "hyde",
                "hypothesis_length": len(hypothesis.split())
            }
        }
```

---

## 🎓 Variações Avançadas

### 1. Multi-HyDE
```python
# Gerar 3 hipóteses diferentes
hyp1 = generate_hypothesis(query, perspective="técnica")
hyp2 = generate_hypothesis(query, perspective="negócio")
hyp3 = generate_hypothesis(query, perspective="usuário")

# Buscar com cada uma
chunks1 = search(hyp1, k=10)
chunks2 = search(hyp2, k=10)
chunks3 = search(hyp3, k=10)

# Fusão (Reciprocal Rank Fusion)
final_chunks = rrf_fusion([chunks1, chunks2, chunks3], k=5)
```

**Benefício**: +10-15% Recall

---

### 2. HyDE Condicional
```python
def smart_hyde(query):
    """
    Usa HyDE apenas quando necessário.
    """
    # Classificar query
    if is_factual_lookup(query):
        return baseline_rag(query)  # Rápido
    elif is_complex_exploratory(query):
        return hyde_rag(query)      # Precisão
    else:
        return baseline_rag(query)  # Default
```

**Benefício**: Reduz custo em 40-60%

---

### 3. HyDE + Reranking
```python
# 1. HyDE retrieval (top-50)
chunks = hyde.retrieve(query, k=50)

# 2. Cross-encoder reranking (top-5)
final_chunks = reranker.rerank(query, chunks, k=5)

# 3. Generation
response = llm.generate(query, final_chunks)
```

**Benefício**: Precision chega a 0.95

---

## 📚 Referências

**Paper Original:**
- Gao et al. (2022) - "Precise Zero-Shot Dense Retrieval without Relevance Labels"
- arXiv:2212.10496

**Implementações:**
- LangChain: `HypotheticalDocumentEmbedder`
- LlamaIndex: `HyDEQueryTransform`

**Benchmarks:**
- BEIR dataset: +12% nDCG@10 vs BM25
- Natural Questions: +8% vs DPR

---

## 🎯 Aprendizados Chave

1. **Resposta > Pergunta**: Documentos são declarativos, não interrogativos
2. **Trade-off Custo vs Precisão**: 2x custo para +20% precisão (vale a pena?)
3. **Prompt Engineering Crítico**: Hipótese genérica = desperdício
4. **Não é Silver Bullet**: Lookup simples não se beneficia
5. **Combina bem**: HyDE + Reranking = excelente

---

## 📈 Progressão de Complexidade

```
Baseline RAG
    ↓
HyDE (você está aqui)
    ↓
    ├─→ Multi-HyDE (múltiplas perspectivas)
    ├─→ HyDE + Reranking (máxima precisão)
    └─→ Conditional HyDE (otimização custo)
```

---

**Técnica Anterior**: [Baseline RAG](./BASELINE_RAG.md)
**Próxima Técnica**: [Reranking](./RERANKING.md)
