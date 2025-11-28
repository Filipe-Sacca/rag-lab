# Adaptive RAG - Seleção Automática da Melhor Técnica

## 📋 Definição

**Adaptive RAG** é um sistema que **analisa automaticamente cada query** e **seleciona dinamicamente a melhor técnica RAG** (ou combinação de técnicas) para aquela query específica.

Ao invés de usar sempre a mesma técnica, o sistema adapta sua estratégia baseado em:
- Complexidade da query
- Tipo de informação necessária
- Requisitos de latência/custo
- Características do domínio

**Insight**: Não existe "melhor técnica RAG universal". A melhor técnica depende da query.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. QUERY ANALYSIS (Classificação)
   ├─ Query: "Qual o telefone da empresa?"
   ├─ LLM analisa características:
   │  ├─ Complexidade: Simples
   │  ├─ Tipo: Factual lookup
   │  ├─ Multi-hop: Não
   │  ├─ Necessita contexto: Mínimo
   │  └─ Fontes: Interna única
   └─ Classificação: "simple_lookup"

2. TECHNIQUE SELECTION (Decisão)
   ├─ Baseado em classificação:
   │  └─ simple_lookup → Baseline RAG
   ├─ Routing rules:
   │  ├─ simple → Baseline
   │  ├─ complex_multi_hop → Sub-Query + Reranking
   │  ├─ ambiguous → HyDE + Reranking
   │  ├─ relational → Graph RAG
   │  └─ maximum_quality → Fusion
   └─ Técnica selecionada: Baseline RAG

3. EXECUTION
   ├─ Executa técnica escolhida
   └─ Retorna resposta

4. FEEDBACK LOOP (Opcional)
   ├─ Avalia qualidade da resposta
   ├─ Se ruim: Tenta técnica mais sofisticada
   └─ Aprende com resultados (ML)
```

### Comparação Visual

**RAG Fixo:**
```
Todas queries → Baseline RAG → Resposta
```

**Adaptive RAG:**
```
Query → Análise
          ↓
    ┌─────┴─────┬──────┬────────┬─────────┐
    ↓           ↓      ↓        ↓         ↓
 Simples    Complexa Ambígua Relacional Multi-fonte
    ↓           ↓      ↓        ↓         ↓
 Baseline   Sub-Query HyDE  Graph RAG   Fusion
    ↓           ↓      ↓        ↓         ↓
         Resposta otimizada por tipo
```

---

## 💡 Por Que Funciona?

### Problema: One-Size-Fits-All

```python
# Usando sempre Fusion (técnica mais avançada):

Query 1: "Qual o telefone?"
→ Fusion: 4 query variations + semantic + BM25
→ Latência: 5s
→ Custo: $0.015
→ Resultado: Telefone correto
❌ Baseline daria mesmo resultado em 1s por $0.001

Query 2: "Compare crescimento A vs B nos últimos 3 anos"
→ Fusion: Múltiplas estratégias, máxima cobertura
→ Latência: 6s
→ Custo: $0.020
→ Resultado: Análise completa
✅ Fusion necessário, Baseline falharia

# Usando sempre Fusion = desperdício 80% do tempo
```

### Solução: Adaptive RAG

```python
# Sistema adaptativo:

Query 1: "Qual o telefone?"
→ Análise: Simple lookup
→ Escolhe: Baseline (rápido, barato)
→ Latência: 1s, Custo: $0.001
✅ Resultado correto com eficiência máxima

Query 2: "Compare crescimento A vs B nos últimos 3 anos"
→ Análise: Complex multi-hop comparative
→ Escolhe: Sub-Query + Reranking
→ Latência: 3s, Custo: $0.008
✅ Resultado completo com técnica apropriada

# Economia: 60-80% custo, 40-60% latência
# Sem perder qualidade
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query Simples

**Query:**
```
"Endereço da matriz"
```

**Análise:**
```python
classifier = QueryClassifier()
features = classifier.analyze("Endereço da matriz")

{
  "complexity": "simple",
  "query_type": "factual_lookup",
  "entities": ["matriz"],
  "multi_hop": false,
  "requires_reasoning": false,
  "ambiguity_score": 0.1,
  "expected_answer_length": "short"
}
```

**Decisão:**
```python
# Routing rules:
if features["complexity"] == "simple" and not features["multi_hop"]:
    technique = "baseline"

# Execução:
response = baseline_rag("Endereço da matriz")
# Latência: 1.2s
# Custo: $0.001
```

---

### Caso 2: Query Ambígua

**Query:**
```
"Como melhorar performance?"
```

**Análise:**
```python
{
  "complexity": "medium",
  "query_type": "open_ended",
  "entities": [],
  "multi_hop": false,
  "requires_reasoning": true,
  "ambiguity_score": 0.8,  # Alta ambiguidade!
  "expected_answer_length": "medium"
}
```

**Decisão:**
```python
# Routing rules:
if features["ambiguity_score"] > 0.7:
    technique = "hyde"  # HyDE resolve ambiguidade

# Execução:
response = hyde_rag("Como melhorar performance?")
# HyDE gera hipótese específica
# Latência: 2.5s
# Custo: $0.004
```

---

### Caso 3: Query Multi-Hop Relacional

**Query:**
```
"Quais colegas do CFO trabalharam na mesma empresa anterior que ele?"
```

**Análise:**
```python
{
  "complexity": "high",
  "query_type": "relational",
  "entities": ["CFO"],
  "multi_hop": true,  # 2+ níveis de relação
  "requires_reasoning": true,
  "ambiguity_score": 0.3,
  "expected_answer_length": "long"
}
```

**Decisão:**
```python
# Routing rules:
if features["query_type"] == "relational" and features["multi_hop"]:
    technique = "graph_rag"  # Grafo resolve multi-hop

# Execução:
response = graph_rag("Quais colegas do CFO...")
# Navega grafo de conhecimento
# Latência: 4s
# Custo: $0.005
```

---

### Caso 4: Query Crítica (Máxima Qualidade)

**Query:**
```
"Análise completa de conformidade legal do produto X"
```

**Análise:**
```python
{
  "complexity": "very_high",
  "query_type": "comprehensive_analysis",
  "entities": ["produto X"],
  "multi_hop": true,
  "requires_reasoning": true,
  "ambiguity_score": 0.4,
  "expected_answer_length": "very_long",
  "domain": "legal",  # Domínio crítico!
  "quality_requirement": "maximum"
}
```

**Decisão:**
```python
# Routing rules:
if features["domain"] == "legal" or features["quality_requirement"] == "maximum":
    technique = "fusion"  # Máxima qualidade

# Execução:
response = fusion_rag("Análise completa conformidade...")
# Múltiplas estratégias, reranking, máxima cobertura
# Latência: 6s
# Custo: $0.020
# Mas qualidade crítica justifica
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Classifier** | LLM-based ou ML model | LLM = simples, ML = rápido |
| **Fallback Strategy** | Progressive enhancement | Se técnica falha, tenta próxima |
| **Quality Threshold** | 0.7 | Se qualidade < 0.7, upgrade técnica |
| **Max Technique Attempts** | 3 | Evita loops infinitos |
| **Learning Enabled** | True | Melhora com feedback |

### Routing Rules (Exemplo)

```python
routing_rules = {
    "simple_lookup": {
        "technique": "baseline",
        "conditions": {
            "complexity": "simple",
            "multi_hop": False,
            "ambiguity_score": "<0.3"
        }
    },

    "ambiguous_query": {
        "technique": "hyde",
        "conditions": {
            "ambiguity_score": ">0.7"
        }
    },

    "multi_hop": {
        "technique": "subquery",
        "conditions": {
            "multi_hop": True,
            "complexity": "medium|high"
        }
    },

    "relational": {
        "technique": "graph_rag",
        "conditions": {
            "query_type": "relational",
            "entities": ">1"
        }
    },

    "maximum_quality": {
        "technique": "fusion",
        "conditions": {
            "domain": ["legal", "medical", "financial"],
            "OR": {
                "quality_requirement": "maximum"
            }
        }
    },

    "default": {
        "technique": "baseline",
        "conditions": {}  # Fallback
    }
}
```

---

## ✅ Vantagens

### 1. Eficiência Massiva
```
Economia vs sempre usar técnica mais avançada:
- Latência: -50-70% (média)
- Custo: -60-80% (média)
- Sem perder qualidade em queries complexas
```

### 2. Qualidade Otimizada por Query
```
Query simples: Baseline (suficiente)
Query complexa: Fusion (necessário)

Resultado: Melhor qualidade média com menor custo
```

### 3. Melhoria Contínua
```python
# Feedback loop:
if response_quality < threshold:
    # Tenta técnica mais sofisticada
    upgrade_technique()

# Machine learning:
# Aprende qual técnica funciona melhor para cada tipo
model.train(query_features, best_technique)
```

### 4. Flexibilidade
```
Fácil adicionar nova técnica:
- Adiciona regra de routing
- Sistema aprende quando usar
- Sem reescrever código existente
```

### 5. Transparência
```
Sistema explica PORQUE escolheu técnica:

"Query classificada como 'multi-hop relational'
 → Usando Graph RAG (melhor para relações)"
```

### 6. Custo-Benefício Ótimo
```
80% queries simples → Baseline ($0.001)
15% queries médias → HyDE/Reranking ($0.004)
5% queries complexas → Fusion/Graph ($0.015)

Custo médio: $0.002 (vs $0.015 sempre Fusion)
Economia: 87%!
```

---

## ❌ Desvantagens

### 1. Overhead de Classificação
```
Baseline simples: 1.2s
Adaptive: 0.3s (classificação) + 1.2s (execução) = 1.5s

❌ Adiciona 0.3s toda query
```

### 2. Complexidade de Manutenção
```
# Precisa manter:
- Todas técnicas RAG
- Sistema de classificação
- Routing rules
- Feedback loop
- ML models (opcional)

Complexidade: Alta
```

### 3. Risco de Classificação Errada
```
Query: "Política de trabalho remoto complexa..."

Classificação (errada): Simple lookup
Técnica escolhida: Baseline
Resultado: Incompleto

❌ Deveria ter usado HyDE ou Sub-Query
```

### 4. Cold Start Problem
```
Primeira execução: Sem dados de feedback
→ Routing rules = heurísticas
→ Pode não ser ótimo

Após 1000 queries: Sistema aprendeu
→ Classificação melhora
→ Mas precisa volume inicial
```

### 5. Custo de Desenvolvimento
```
Implementar Adaptive RAG:
- 2-3 semanas vs 1 semana RAG fixo
- Precisa dataset de queries para treinar
- Testes extensivos de routing rules
```

### 6. Latência Imprevisível
```
Query A: Baseline → 1s
Query B: Fusion → 6s

❌ Dificulta SLA fixo
```

---

## 📊 Métricas Esperadas

### Comparação: Sempre Fusion vs Adaptive

| Métrica | Sempre Fusion | Adaptive RAG | Δ |
|---------|---------------|--------------|---|
| **Avg Latência** | 5.5s | 2.2s | -60% ⭐ |
| **Avg Custo/Query** | $0.018 | $0.004 | -78% ⭐ |
| **Quality (Simple)** | 0.90 | 0.88 | -2% |
| **Quality (Complex)** | 0.95 | 0.93 | -2% |
| **Overall Quality** | 0.91 | 0.89 | -2% |

**Trade-off**: -2% qualidade para -60% latência e -78% custo = ótimo!

### Distribuição de Técnicas (Exemplo Real)

```
1000 queries analisadas:

Baseline:     650 queries (65%) - simples, lookup
HyDE:         150 queries (15%) - ambíguas
Reranking:     80 queries (8%)  - precisão crítica
Sub-Query:     70 queries (7%)  - multi-hop
Fusion:        30 queries (3%)  - máxima qualidade
Graph RAG:     20 queries (2%)  - relacional

Economia vs sempre Fusion:
- 97% das queries usam técnica mais barata
- 3% usam técnica cara (quando necessário)
```

---

## 🎯 Quando Usar Adaptive RAG

### ✅ Casos Ideais

**1. Queries Heterogêneas**
```
✅ Chatbot geral (tipos variados)
✅ Search engine (lookups + análises)
✅ Assistente corporativo (simples + complexo)
```

**2. Budget Limitado com Alta Qualidade Necessária**
```
✅ Startups (economizar 80%)
✅ Alto volume (>10K queries/dia)
✅ Mas não pode sacrificar qualidade totalmente
```

**3. Latência Variável Aceitável**
```
✅ Async workflows (não real-time)
✅ Background jobs
✅ Research assistants
```

**4. Capacidade de Manter Múltiplas Técnicas**
```
✅ Time de engenharia dedicado
✅ Infraestrutura robusta
✅ CI/CD para múltiplos pipelines
```

**5. Volume Suficiente para Aprendizado**
```
✅ >1K queries/dia
✅ Dados para treinar classifier
✅ Feedback loop viável
```

---

### ❌ Quando NÃO Usar

**1. Queries Homogêneas**
```
❌ Documentação técnica (sempre mesmo tipo)
❌ FAQ system (sempre lookups)
→ Use técnica fixa otimizada
```

**2. Latência Crítica Fixa**
```
❌ SLA <2s garantido
❌ Real-time chat
→ Adaptive = imprevisível (1-6s)
```

**3. Equipe Pequena**
```
❌ 1-2 devs
❌ Não pode manter múltiplas técnicas
→ Use RAG fixo (Baseline ou HyDE)
```

**4. MVP / Prototipagem**
```
❌ Precisa validar em 1 semana
❌ Complexidade = overhead desnecessário
→ Comece simples, adicione Adaptive depois
```

**5. Baixo Volume**
```
❌ <100 queries/dia
❌ Não justifica complexidade
→ Use técnica fixa de qualidade média-alta
```

---

## 🔬 Experimentos Recomendados

### 1. Query Classification Accuracy
```python
# Dataset: 1000 queries com técnica ótima anotada
# Medir: Precision, Recall de classificador
# Objetivo: >90% accuracy
```

### 2. Cost-Quality Trade-off
```python
# Testar diferentes thresholds para upgrade:
# - Conservative: Usa técnica cara frequentemente
# - Aggressive: Usa técnica barata ao máximo
# Medir: Custo vs RAGAS scores
```

### 3. Fallback Strategy Effectiveness
```python
# Quando técnica escolhida falha:
# - Strategy A: Tenta próxima técnica
# - Strategy B: Tenta técnica mais avançada
# Medir: Recovery rate
```

---

## 💻 Estrutura de Código

```python
# adaptive_rag.py

from typing import Dict, Callable
import numpy as np

class AdaptiveRAG:
    """
    Sistema adaptativo que seleciona melhor técnica RAG.

    Pipeline:
    1. Classify query
    2. Select technique
    3. Execute
    4. Evaluate & learn
    """

    def __init__(self, techniques: Dict[str, Callable], llm):
        self.techniques = techniques  # {name: function}
        self.llm = llm
        self.classifier = QueryClassifier(llm)
        self.router = TechniqueRouter()
        self.feedback_store = []

    def classify_query(self, query: str) -> Dict:
        """
        Classifica query em features.
        """
        prompt = f"""
Analise esta query e extraia características:

Query: "{query}"

Retorne JSON:
{{
  "complexity": "simple" | "medium" | "high" | "very_high",
  "query_type": "factual_lookup" | "analysis" | "relational" | "comparison" | "open_ended",
  "multi_hop": true | false,
  "ambiguity_score": 0.0-1.0,
  "entities_count": number,
  "expected_answer_length": "short" | "medium" | "long"
}}
"""
        response = self.llm.invoke(prompt, temperature=0.0)
        features = json.loads(response.content)
        return features

    def select_technique(self, features: Dict) -> str:
        """
        Seleciona técnica baseado em features.
        """
        # Routing rules
        if features["complexity"] == "simple" and not features["multi_hop"]:
            return "baseline"

        if features["ambiguity_score"] > 0.7:
            return "hyde"

        if features["multi_hop"] and features["entities_count"] > 1:
            if features["query_type"] == "relational":
                return "graph_rag"
            else:
                return "subquery"

        if features["complexity"] == "very_high":
            return "fusion"

        # Reranking para queries de precisão média-alta
        if features["complexity"] in ["medium", "high"]:
            return "reranking"

        # Default
        return "baseline"

    def execute_technique(self, technique: str, query: str) -> Dict:
        """
        Executa técnica selecionada.
        """
        if technique not in self.techniques:
            # Fallback
            technique = "baseline"

        start_time = time.time()
        result = self.techniques[technique](query)
        latency = time.time() - start_time

        return {
            "response": result["response"],
            "technique_used": technique,
            "latency": latency,
            **result.get("metrics", {})
        }

    def evaluate_quality(self, query: str, response: str, chunks: list) -> float:
        """
        Avalia qualidade da resposta (simplificado).
        """
        # Usar RAGAS ou heurística simples
        prompt = f"""
Avalie a qualidade desta resposta (0.0-1.0):

Query: {query}
Resposta: {response}

Score (0.0-1.0):
"""
        score_response = self.llm.invoke(prompt)
        score = float(score_response.content.strip())
        return score

    def query(self, query: str, quality_threshold: float = 0.7) -> Dict:
        """
        Pipeline completo adaptativo.
        """
        start_time = time.time()

        # 1. Classify
        t1 = time.time()
        features = self.classify_query(query)
        classify_time = time.time() - t1

        # 2. Select technique
        technique = self.select_technique(features)

        # 3. Execute
        t2 = time.time()
        result = self.execute_technique(technique, query)
        execute_time = time.time() - t2

        # 4. Evaluate quality
        quality_score = self.evaluate_quality(
            query,
            result["response"],
            result.get("chunks", [])
        )

        # 5. Fallback se qualidade baixa
        if quality_score < quality_threshold and technique != "fusion":
            # Tenta técnica mais avançada
            upgraded_technique = self._upgrade_technique(technique)

            result = self.execute_technique(upgraded_technique, query)
            quality_score = self.evaluate_quality(
                query,
                result["response"],
                result.get("chunks", [])
            )

            result["technique_used"] = f"{technique} → {upgraded_technique} (upgraded)"

        total_latency = time.time() - start_time

        # 6. Store feedback para aprendizado
        self.feedback_store.append({
            "query": query,
            "features": features,
            "technique": result["technique_used"],
            "quality_score": quality_score,
            "latency": total_latency
        })

        return {
            "response": result["response"],
            "technique_used": result["technique_used"],
            "query_features": features,
            "quality_score": quality_score,
            "metrics": {
                "latency_total": total_latency,
                "latency_classify": classify_time,
                "latency_execute": execute_time,
                "technique": "adaptive_rag"
            }
        }

    def _upgrade_technique(self, current: str) -> str:
        """
        Upgrade para técnica mais sofisticada.
        """
        upgrade_path = {
            "baseline": "reranking",
            "hyde": "reranking",
            "reranking": "fusion",
            "subquery": "fusion",
            "graph_rag": "fusion",
            "fusion": "fusion"  # Já é o máximo
        }
        return upgrade_path.get(current, "fusion")

    def get_statistics(self) -> Dict:
        """
        Estatísticas de uso de técnicas.
        """
        technique_counts = {}
        total_cost = 0
        total_latency = 0

        for record in self.feedback_store:
            tech = record["technique"]
            technique_counts[tech] = technique_counts.get(tech, 0) + 1
            total_latency += record["latency"]

        return {
            "total_queries": len(self.feedback_store),
            "technique_distribution": technique_counts,
            "avg_latency": total_latency / len(self.feedback_store) if self.feedback_store else 0,
            "avg_quality": np.mean([r["quality_score"] for r in self.feedback_store]) if self.feedback_store else 0
        }
```

---

## 🎓 Variações Avançadas

### 1. ML-Based Classification
```python
from sklearn.ensemble import RandomForestClassifier

class MLQueryClassifier:
    """
    Classifier treinado com dados históricos.
    """
    def __init__(self):
        self.model = RandomForestClassifier()
        self.trained = False

    def train(self, queries, optimal_techniques):
        """
        Treina com queries passadas e técnica ótima.
        """
        X = [self.extract_features(q) for q in queries]
        y = optimal_techniques

        self.model.fit(X, y)
        self.trained = True

    def predict(self, query):
        """
        Prediz melhor técnica.
        """
        features = self.extract_features(query)
        technique = self.model.predict([features])[0]
        return technique

    def extract_features(self, query):
        """
        Features numéricas para ML.
        """
        return [
            len(query.split()),  # word count
            query.count("?"),    # question marks
            len(set(query.split())),  # unique words
            # ... mais features
        ]
```

### 2. A/B Testing Framework
```python
def adaptive_with_ab_testing(query):
    """
    Testa múltiplas técnicas, aprende qual melhor.
    """
    if random() < 0.1:  # 10% das queries
        # Teste: Executa 2 técnicas
        technique_a = select_technique(query)
        technique_b = random_alternative(technique_a)

        result_a = execute(technique_a, query)
        result_b = execute(technique_b, query)

        # Usuário escolhe qual melhor (ou RAGAS)
        winner = evaluate_winner(result_a, result_b)

        # Aprende
        update_model(query, winner)

        return result_a  # Retorna padrão
    else:
        # Normal: Usa modelo treinado
        return adaptive_rag(query)
```

---

## 📚 Referências

**Papers:**
- Jeong et al. (2024) - "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models"
- Asai et al. (2024) - "Self-RAG: Learning to Retrieve, Generate and Critique"

**Implementações:**
- LangChain: Router chains
- LlamaIndex: Query routing

---

## 🎯 Aprendizados Chave

1. **Context-Aware RAG**: Melhor técnica depende do contexto
2. **80/20 Rule**: 80% queries = simples (baseline suficiente)
3. **Trade-off Aceitável**: -2% qualidade por -70% custo/latência
4. **Melhoria Contínua**: Sistema aprende com feedback
5. **Production Essential**: Adaptive é futuro para sistemas em escala

---

**Técnica Anterior**: [Agentic RAG](./AGENTIC_RAG.md)
**Resumo Comparativo**: [COMPARISON.md](./COMPARISON.md) *(próximo)*
