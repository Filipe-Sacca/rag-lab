# Agentic RAG - RAG como Ferramenta de um Agente Inteligente

## 📋 Definição

**Agentic RAG** transforma RAG de um **pipeline fixo** em uma **ferramenta opcional** que um agente de IA pode **decidir usar ou não**, junto com outras ferramentas (web search, calculator, APIs).

O agente usa **raciocínio ReAct** (Reasoning and Acting) para determinar:
- **SE** precisa fazer RAG
- **QUANDO** fazer RAG
- **COMO** formular a query para RAG
- **COMBINAR** RAG com outras ferramentas

**Insight**: Nem toda pergunta precisa de RAG. Um agente inteligente sabe quando usar cada ferramenta.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. USER QUERY
   ├─ Query: "Qual o preço da ação da Apple hoje e como isso se compara ao lucro do último trimestre da nossa empresa?"

2. AGENT REASONING (ReAct Loop)
   ├─ Thought 1: "Preciso de 2 informações:"
   │  ├─ Preço ação Apple (tempo real, externa)
   │  └─ Lucro nossa empresa (interna, documentos)
   │
   ├─ Action 1: tool_web_search["preço ação Apple hoje"]
   ├─ Observation 1: "$185.50 (fechamento hoje)"
   │
   ├─ Thought 2: "Agora preciso do lucro interno"
   ├─ Action 2: tool_internal_rag["lucro último trimestre"]
   ├─ Observation 2: "Lucro Q3: R$ 3 bilhões"
   │
   ├─ Thought 3: "Tenho todas informações, posso responder"
   └─ Final Answer: "Apple: $185.50. Nosso lucro Q3: R$ 3bi..."

3. RESPONSE
   └─ Resposta sintetizada de múltiplas fontes
```

### Comparação Visual

**RAG Tradicional (Pipeline Fixo):**
```
Query → SEMPRE faz RAG → LLM → Resposta
                ↓
        Mesmo se não precisar
```

**Agentic RAG (Decisão Inteligente):**
```
Query → Agent analisa
           ↓
    ┌──────┴──────┬──────────┬──────────┐
    ↓             ↓          ↓          ↓
  RAG?      Web Search?  Calculator? Direct Answer?
    ↓             ↓          ↓          ↓
  Usa ferramentas APENAS quando necessário
    ↓
  Combina resultados → Resposta
```

---

## 💡 Por Que Funciona?

### Problema do RAG Fixo

```python
# Pipeline RAG tradicional:

def rag_pipeline(query):
    chunks = vector_search(query)  # SEMPRE executa
    response = llm.generate(query, chunks)
    return response

# Problemas:

Query 1: "Qual o telefone da empresa?"
→ Busca no Vector DB (necessário) ✅
→ Retorna: "(11) 1234-5678"

Query 2: "Quanto é 2 + 2?"
→ Busca no Vector DB (desnecessário!) ❌
→ Retorna chunks irrelevantes sobre matemática
→ LLM responde "4" (mas gastou busca à toa)

Query 3: "Preço da ação da Apple hoje?"
→ Busca no Vector DB (dados internos) ❌
→ Não acha (dados externos/tempo real)
→ LLM: "Não tenho essa informação"

❌ RAG fixo = burro
```

### Solução Agentic RAG

```python
# Agent com múltiplas ferramentas:

tools = {
    "internal_rag": buscar_documentos_internos,
    "web_search": buscar_na_internet,
    "calculator": fazer_calculos,
    "sql_query": consultar_banco_dados
}

# Agent decide:

Query 1: "Qual o telefone?"
→ Thought: "Info interna, usar RAG"
→ Action: internal_rag["telefone"]
✅ Escolha correta

Query 2: "Quanto é 2 + 2?"
→ Thought: "Cálculo simples, não precisa RAG"
→ Action: calculator["2+2"]
✅ Sem desperdício

Query 3: "Preço ação Apple hoje?"
→ Thought: "Dado externo e atual, preciso web"
→ Action: web_search["Apple stock price today"]
✅ Fonte correta

Query 4: "Preço ação Apple vs nosso lucro?"
→ Thought: "Preciso combinar web + RAG"
→ Action 1: web_search["Apple price"]
→ Action 2: internal_rag["nosso lucro"]
→ Final Answer: Sintetiza ambos
✅ Multi-tool reasoning
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Query que NÃO Precisa de RAG

**Query:**
```
"Quantos dias úteis tem entre 15/nov e 30/nov?"
```

**RAG Tradicional (Desperdício):**
```python
# 1. Busca no Vector DB
chunks = search("dias úteis novembro")
# Retorna: Políticas de férias, calendários antigos...

# 2. LLM tenta responder com chunks irrelevantes
response = llm.generate(query, chunks)
# "Com base nos documentos... [tenta adivinhar]"

❌ Custo: 1 busca vetorial + chunks irrelevantes
❌ Precisão: Baixa (LLM inventando)
```

**Agentic RAG (Inteligente):**
```python
# Agent ReAct Loop:

Thought: "Esta é uma pergunta de cálculo de data.
          Não preciso de documentos internos.
          Posso calcular diretamente."

Action: calculator["count_business_days(2024-11-15, 2024-11-30)"]

Observation: "11 dias úteis"

Final Answer: "Entre 15/nov e 30/nov há 11 dias úteis."

✅ Custo: Zero RAG, apenas cálculo
✅ Precisão: 100%
```

---

### Caso 2: Query Multi-Fonte

**Query:**
```
"Compare o crescimento de receita da nossa empresa com o crescimento da Apple no último ano"
```

**RAG Tradicional (Incompleto):**
```python
# RAG só acessa dados internos
chunks = search("crescimento receita último ano")
# Retorna: Nosso crescimento = 15%

response = llm.generate(query, chunks)
# "Nossa receita cresceu 15%. Não tenho dados da Apple."

❌ Resposta incompleta
```

**Agentic RAG (Completo):**
```python
# Agent ReAct Loop:

Thought: "Preciso de 2 dados:
          1. Nosso crescimento (interno) → RAG
          2. Crescimento Apple (externo) → Web Search"

Action 1: internal_rag["crescimento receita último ano nossa empresa"]
Observation 1: "Crescimento: 15%"

Thought: "Tenho nosso dado, agora preciso da Apple"

Action 2: web_search["Apple revenue growth last year 2024"]
Observation 2: "Apple revenue grew 8% in fiscal 2024"

Thought: "Tenho ambos, posso comparar"

Final Answer: "Nossa empresa cresceu 15% vs Apple 8%.
               Crescemos quase 2x mais que a Apple no último ano."

✅ Multi-fonte: RAG + Web Search
✅ Resposta completa e comparativa
```

---

### Caso 3: Query que Precisa Apenas de RAG

**Query:**
```
"Qual foi o investimento em P&D no Q3?"
```

**Agentic RAG:**
```python
Thought: "Dado interno específico.
          Não é cálculo, não é dado externo.
          Preciso usar RAG interno."

Action: internal_rag["investimento P&D Q3"]

Observation: "Investimento P&D Q3: R$ 800 milhões"

Final Answer: "O investimento em P&D no Q3 foi R$ 800 milhões."

✅ Usa RAG quando apropriado
✅ Não tenta outras ferramentas desnecessariamente
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Agent Type** | ReAct (Reasoning + Acting) | Explica raciocínio |
| **Max Iterations** | 5-10 | Evita loops infinitos |
| **Tool Timeout** | 30s por ferramenta | Evita travamentos |
| **LLM (Agent Brain)** | GPT-4 / Gemini Pro | Precisa raciocínio forte |
| **Tool LLM** | GPT-3.5 / Gemini Flash | Ferramentas podem usar modelo menor |

### Ferramentas Comuns

| Ferramenta | Descrição | Quando Usar |
|------------|-----------|-------------|
| **internal_rag** | Busca documentos internos | Dados da empresa |
| **web_search** | Google/Bing search | Dados públicos/atuais |
| **calculator** | Operações matemáticas | Cálculos, datas |
| **sql_query** | Query banco de dados | Dados estruturados |
| **api_call** | Chamar APIs externas | Integração sistemas |
| **python_repl** | Executar código Python | Análise de dados |

---

## ✅ Vantagens

### 1. Eficiência Massiva
```
RAG Tradicional: 100% queries fazem busca vetorial
Agentic RAG: ~40% queries fazem busca

Economia: 60% nas chamadas ao Vector DB
```

### 2. Multi-Fonte Nativo
```
✅ Combina RAG + Web Search + APIs
✅ Responde queries impossíveis para RAG fixo
✅ Dados internos + externos integrados
```

### 3. Custo-Efetivo
```
Query: "Quanto é 10% de 1000?"

RAG Fixo:
- Busca vetorial: $0.0001
- LLM com chunks: $0.002
Total: $0.0021

Agentic:
- Calculator direto: $0
- LLM agent reasoning: $0.0005
Total: $0.0005 (76% economia)
```

### 4. Raciocínio Explícito
```
Agent mostra COMO chegou na resposta:

Thought: "Preciso de dados externos"
Action: web_search[...]
Observation: [resultado]
Final Answer: [resposta]

✅ Transparência
✅ Debuggável
✅ Usuário entende processo
```

### 5. Falha Mais Graceful
```
RAG Fixo: Não acha no Vector DB → "Não sei"

Agentic: Não acha no RAG → Tenta web_search
        → Tenta outra fonte
        → Múltiplas tentativas antes de desistir
```

### 6. Escalável em Ferramentas
```python
# Adicionar nova ferramenta = trivial:
agent.tools.append({
    "name": "weather_api",
    "description": "Get current weather",
    "function": get_weather
})

# Agent aprende a usar automaticamente
```

---

## ❌ Desvantagens

### 1. Latência Variável e Imprevisível
```
Query simples: "Telefone?"
→ Agent: 1 iteration → 2s

Query complexa: "Compare dados A, B, C"
→ Agent: 5 iterations → 15s (!)

❌ Latência imprevisível (1-20s)
❌ Dificulta SLA
```

### 2. Custo LLM Maior
```
RAG Fixo:
- 1 chamada LLM (geração)

Agentic RAG:
- 1 chamada (reasoning)
- 1 chamada (action planning)
- 1 chamada (synthesis)
- ...potencialmente 5-10 chamadas LLM

Custo: 3-10x maior por query complexa
```

### 3. Risco de Loops e Errors
```python
# Agent pode entrar em loop:

Thought: "Preciso de dado X"
Action: web_search[X]
Observation: "Não encontrado"

Thought: "Vou tentar de novo"
Action: web_search[X]  # Mesmo que antes!
Observation: "Não encontrado"

# Repete 10x até timeout
❌ Desperdiça tempo e custo
```

### 4. Dependência de Qualidade do LLM
```
LLM fraco (GPT-3.5):
→ Raciocínio ruim
→ Escolhe ferramenta errada
→ Loops frequentes

LLM forte (GPT-4):
→ Raciocínio bom
→ Escolhas corretas
→ Mas 10x mais caro

❌ Trade-off qualidade vs custo
```

### 5. Complexidade de Debug
```
RAG Fixo: Query → Chunks → Resposta
         ↓ Fácil debugar

Agentic: Query →
         ↓ Thought 1 → Action 1 → Obs 1
         ↓ Thought 2 → Action 2 → Obs 2
         ↓ Thought 3 → Action 3 → Obs 3
         ↓ Final Answer

❌ Difícil rastrear ONDE falhou
❌ Muitos pontos de falha
```

### 6. Não Garante Uso de RAG
```
Query: "Política de férias"

Agent (erroneamente):
Thought: "Posso responder do meu conhecimento"
Final Answer: [Inventa política genérica]

❌ Deveria ter usado RAG
❌ Agent "pulou" ferramenta necessária
```

---

## 📊 Métricas Esperadas

### Comparação RAG Fixo vs Agentic

| Métrica | RAG Fixo | Agentic RAG | Δ |
|---------|----------|-------------|---|
| **Success Rate** | 70-80% | 85-95% | +15-20% |
| **Multi-Source Queries** | 0% | 90%+ | N/A |
| **Avg Latency** | 2s (fixo) | 2-8s (variável) | -3x |
| **Avg Custo/Query** | $0.002 | $0.005-0.015 | 3-7x |
| **RAG Usage Rate** | 100% | 30-50% | -50% |

### RAGAS Scores (Queries Apropriadas)

| Métrica | RAG Fixo | Agentic | Δ |
|---------|----------|---------|---|
| **Faithfulness** | 0.80 | 0.90 | +12% |
| **Answer Relevancy** | 0.75 | 0.92 | +23% |
| **Tool Selection Accuracy** | N/A | 0.88 | - |

---

## 🎯 Quando Usar Agentic RAG

### ✅ Casos Ideais

**1. Queries Diversas e Imprevisíveis**
```
✅ Chatbot geral (não sabe tipo de pergunta)
✅ Assistente executivo (dados internos + externos)
✅ Research assistant (múltiplas fontes)
```

**2. Multi-Domínio**
```
✅ "Preço ação Apple" (web) + "Nosso lucro" (RAG) + "Comparar" (calculator)
✅ Dados internos + externos + cálculos
```

**3. Baixo Volume, Alta Complexidade**
```
✅ <1K queries/dia
✅ Cada query vale muito (decisões executivas)
✅ Budget OK com $5-10/dia
```

**4. Necessidade de Rastreabilidade**
```
✅ Compliance, audit (precisa ver raciocínio)
✅ Transparência em decisões
✅ Debugging de respostas
```

**5. Integração com Múltiplos Sistemas**
```
✅ RAG + CRM + ERP + Web
✅ Orquestração de ferramentas
```

---

### ❌ Quando NÃO Usar

**1. Queries Previsíveis e Homogêneas**
```
❌ FAQ system (sempre usa RAG)
❌ Documentação técnica (sempre RAG)
→ RAG fixo é suficiente e mais rápido
```

**2. Latência Crítica**
```
❌ SLA <2s
❌ Real-time chat
❌ Autocomplete
→ Agentic = imprevisível (1-15s)
```

**3. Alto Volume de Queries**
```
❌ >10K queries/dia
❌ Custo 5x RAG fixo = $50+/dia
→ Inviável economicamente
```

**4. LLM Fraco Disponível**
```
❌ Só tem acesso a GPT-3.5 ou modelos locais fracos
→ Raciocínio ruim = agent inútil
```

**5. Requisito de Determinismo**
```
❌ Precisa garantir sempre usa RAG
❌ Não pode "pular" busca interna
→ RAG fixo = previsível
```

---

## 🔬 Experimentos Recomendados

### 1. Tool Usage Analysis
```python
# Medir: Quais ferramentas são usadas com que frequência
# Dataset: 1000 queries diversas
# Métrica: % uso de cada tool
# Insight: Otimizar tools mais usados
```

### 2. LLM Model Comparison
```python
# Testar: GPT-4, GPT-3.5, Gemini Pro, Claude
# Medir: Tool selection accuracy, cost, latency
# Hipótese: GPT-4 melhor mas 10x mais caro
```

### 3. Max Iterations Impact
```python
# Testar: max_iter = 3, 5, 10, 20
# Medir: Success rate vs latency
# Hipótese: 5-7 iterations = sweet spot
```

---

## 💻 Estrutura de Código (LangGraph)

```python
# agentic_rag.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    """Estado do agente durante execução"""
    query: str
    thoughts: Annotated[list, operator.add]
    actions: Annotated[list, operator.add]
    observations: Annotated[list, operator.add]
    final_answer: str
    iterations: int

# Definir ferramentas
def internal_rag(query: str) -> str:
    """Busca documentos internos"""
    chunks = vector_search(query)
    return f"Chunks encontrados: {chunks}"

def web_search(query: str) -> str:
    """Busca na web"""
    results = google_search(query)
    return f"Resultados: {results}"

def calculator(expression: str) -> str:
    """Calcula expressão matemática"""
    result = eval(expression)
    return f"Resultado: {result}"

tools = {
    "internal_rag": internal_rag,
    "web_search": web_search,
    "calculator": calculator
}

# Nós do grafo
def reasoning_node(state: AgentState) -> AgentState:
    """Agent pensa sobre próximo passo"""

    prompt = f"""
Você é um agente inteligente com as seguintes ferramentas:
{list(tools.keys())}

Query do usuário: {state['query']}

Histórico:
Thoughts: {state['thoughts']}
Actions: {state['actions']}
Observations: {state['observations']}

Próximo passo:
1. Se você tem informação suficiente → Final Answer: [resposta]
2. Caso contrário → Thought: [raciocínio] | Action: tool_name[input]

Formato: Thought: ... | Action: ... OU Final Answer: ...
"""

    response = llm.invoke(prompt)

    if "Final Answer:" in response:
        state["final_answer"] = response.split("Final Answer:")[1].strip()
    else:
        thought, action = response.split("|")
        state["thoughts"].append(thought.strip())
        state["actions"].append(action.strip())

    state["iterations"] += 1
    return state

def action_node(state: AgentState) -> AgentState:
    """Executa ação escolhida pelo agent"""

    if not state["actions"]:
        return state

    last_action = state["actions"][-1]

    # Parse: "Action: tool_name[input]"
    tool_name = last_action.split("[")[0].split(":")[-1].strip()
    tool_input = last_action.split("[")[1].split("]")[0]

    # Executar ferramenta
    if tool_name in tools:
        observation = tools[tool_name](tool_input)
        state["observations"].append(observation)
    else:
        state["observations"].append(f"Erro: Tool {tool_name} não existe")

    return state

def should_continue(state: AgentState) -> str:
    """Decide se continua ou termina"""

    if state["final_answer"]:
        return "end"

    if state["iterations"] >= 10:
        return "end"  # Max iterations

    return "continue"

# Construir grafo
workflow = StateGraph(AgentState)

# Adicionar nós
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("action", action_node)

# Adicionar arestas
workflow.set_entry_point("reasoning")
workflow.add_edge("reasoning", "action")
workflow.add_conditional_edges(
    "action",
    should_continue,
    {
        "continue": "reasoning",
        "end": END
    }
)

# Compilar
agent = workflow.compile()

# Executar
def query_agentic_rag(query: str) -> dict:
    """
    Executa Agentic RAG completo.
    """
    start_time = time.time()

    initial_state = {
        "query": query,
        "thoughts": [],
        "actions": [],
        "observations": [],
        "final_answer": "",
        "iterations": 0
    }

    # Executar grafo
    final_state = agent.invoke(initial_state)

    latency = time.time() - start_time

    return {
        "response": final_state["final_answer"],
        "reasoning_trace": {
            "thoughts": final_state["thoughts"],
            "actions": final_state["actions"],
            "observations": final_state["observations"]
        },
        "metrics": {
            "latency": latency,
            "iterations": final_state["iterations"],
            "tools_used": len(final_state["actions"]),
            "technique": "agentic_rag"
        }
    }
```

---

## 📚 Referências

**Papers:**
- Yao et al. (2023) - "ReAct: Synergizing Reasoning and Acting in Language Models"
- Shinn et al. (2023) - "Reflexion: Language Agents with Verbal Reinforcement Learning"

**Frameworks:**
- LangGraph (LangChain) - Graph-based agent orchestration
- AutoGPT - Autonomous agent framework
- AgentGPT - Web-based agent platform

**Benchmarks:**
- ToolBench: Tool selection accuracy
- HotPotQA: Multi-hop reasoning

---

## 🎯 Aprendizados Chave

1. **RAG = Ferramenta, Não Pipeline**: Agent decide quando usar
2. **Multi-Tool Reasoning**: Combina fontes impossíveis para RAG fixo
3. **Trade-off Custo/Qualidade**: 5x custo para +20% success rate
4. **Transparência**: ReAct mostra raciocínio explícito
5. **Futuro do RAG**: Agentic é evolução natural, mas não substitui RAG fixo totalmente

---

**Técnica Anterior**: [Parent Document](./PARENT_DOCUMENT.md)
**Próxima Técnica**: [Adaptive RAG](./ADAPTIVE_RAG.md)
