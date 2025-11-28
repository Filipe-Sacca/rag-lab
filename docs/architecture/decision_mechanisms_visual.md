# Decision Mechanisms Visual Comparison

## Side-by-Side Architecture

### ADAPTIVE RAG - Linear DAG

```
┌─────────────────────────────────────────────────────────────────┐
│  ADAPTIVE RAG ARCHITECTURE (Classifier-based routing)            │
└─────────────────────────────────────────────────────────────────┘

        Query Input
            │
            ▼
    ┌───────────────────┐
    │ 1. CLASSIFICATION │  ← LLM Call #1
    ├───────────────────┤
    │ "What is Python?" │
    │      ↓            │
    │   "simple"        │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ 2. ROUTING        │  ← Rule Lookup (Dict)
    ├───────────────────┤
    │ "simple" → ?      │
    │      ↓            │
    │ "baseline"        │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ 3. EXECUTION      │  ← LLM Call #2
    ├───────────────────┤
    │ baseline_rag()    │
    │      ↓            │
    │  Answer + Src     │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ 4. RESPONSE       │  ← Packaging
    ├───────────────────┤
    │ Details +         │
    │ Metrics           │
    └───────────────────┘
            │
            ▼
        Output

Performance: 1.2-3.5s | Deterministic | Single-path
```

### AGENTIC RAG - Iterative Loop

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENTIC RAG ARCHITECTURE (Agent-based reasoning)                │
└─────────────────────────────────────────────────────────────────┘

        Query Input
            │
            ▼
    ┌─────────────────────┐
    │ AGENT REASONING     │  ← LLM Call #1
    ├─────────────────────┤
    │ "What is Python?"   │
    │ System Prompt:      │
    │ - Tools available   │
    │ - Techniques ready  │
    │       ↓             │
    │ "Call internal_rag" │  ← Decides with tool binding
    │ [tool_calls]        │
    └─────────────────────┘
            │
            ▼
    ┌─────────────────────┐
    │ SHOULD CONTINUE?    │  ← Conditional
    ├─────────────────────┤
    │ tool_calls exist?   │
    │    YES → "tools"    │
    │    NO  → "end"      │
    └─────────────────────┘
            │
        ┌───┴───┐
        │       │
        YES     NO
        │       │
        ▼       ▼
    ┌─────┐ ┌──────────┐
    │TOOL │ │EXTRACT   │
    ├─────┤ ├──────────┤
    │Execute│ Answer +  │
    │RAG   │ Sources   │
    │      │           │
    │result├──────────┤
    └─────┘ Output
        │
        └──→ LOOP BACK to
            AGENT REASONING
            (if needed)

Performance: 2.5-7.0s | Dynamic | Multi-path
```

---

## Decision Mechanism Comparison

### How Decisions are Made

```
ADAPTIVE RAG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query
  │
  ├─→ [Step 1] LLM Classification
  │   Input: "What is the capital of France?"
  │   Prompt: "Classify as simple/complex/abstract/precision"
  │   Output: "simple" (text extraction)
  │
  ├─→ [Step 2] Static Mapping
  │   lookup("simple")
  │   → CATEGORY_TO_TECHNIQUE["simple"]
  │   → "baseline"
  │   (No reasoning, just dict lookup)
  │
  └─→ Fixed path for this query type


AGENTIC RAG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query
  │
  ├─→ [Iteration 1] Agent Reasoning
  │   Input: "What is the capital of France?"
  │   Tools: [internal_rag_tool, web_search_tool]
  │   Techniques: [baseline, hyde, reranking]
  │   
  │   Agent thinks:
  │   "This is a factual question about geography...
  │    I should search the internal database first
  │    with baseline technique for speed"
  │   
  │   Decision: Call internal_rag_tool(technique="baseline")
  │   (LLM reasoning with tool understanding)
  │
  ├─→ [Tool Execution]
  │   Run the chosen tool
  │   Get: answer + sources + metrics
  │
  ├─→ [Iteration 2?] Agent Analyzes Results
  │   Previous tool gave: "Paris is the capital"
  │   Think: "I have a complete answer"
  │   Decision: No more tools needed
  │   → should_continue() returns "end"
  │
  └─→ Flexible path, decided dynamically
```

---

## Classification Examples Visual

```
ADAPTIVE RAG - 4 Fixed Categories

Query: "What is Python?"
├─ Indicators: Direct question
├─ LLM Output: "simple"
├─ Confidence: 0.90 (fixed)
└─ Route: simple → baseline
   └─ Latency: ~1.2s
   └─ Cost: $0.003

Query: "Compare Python vs JavaScript"
├─ Indicators: "Compare" verb
├─ LLM Output: "complex"
├─ Confidence: 0.90 (fixed)
└─ Route: complex → subquery
   └─ Latency: ~3.5s
   └─ Cost: $0.008

Query: "How does ML work?"
├─ Indicators: "How" + conceptual
├─ LLM Output: "abstract"
├─ Confidence: 0.90 (fixed)
└─ Route: abstract → hyde
   └─ Latency: ~2.5s
   └─ Cost: $0.004

Query: "HIPAA compliance requirements?"
├─ Indicators: Legal/technical domain
├─ LLM Output: "precision"
├─ Confidence: 0.90 (fixed)
└─ Route: precision → reranking
   └─ Latency: ~2.5s
   └─ Cost: $0.003


AGENTIC RAG - Dynamic Agent Decision

Query: "What is Python?"
├─ Agent: "Factual question, use RAG"
├─ Tool: internal_rag_tool
├─ Technique: baseline (agent-selected)
├─ Result: Complete
├─ Iterations: 1
└─ Latency: ~2.5s

Query: "Compare Python vs JavaScript"
├─ Agent: "Need comparison, use RAG"
├─ Tool 1: internal_rag_tool(hyde)
├─ Result 1: Good comparison
├─ Agent: "Sufficient info"
├─ Iterations: 1-2
└─ Latency: ~3.8s

Query: "How does ML work?"
├─ Agent: "Abstract question, explain"
├─ Tool 1: internal_rag_tool(hyde)
├─ Result 1: Explains concepts
├─ Agent: "Good explanation"
├─ Iterations: 1
└─ Latency: ~3.2s

Query: "What's new in Python 3.13?"
├─ Agent: "Might be outdated in docs"
├─ Tool 1: internal_rag_tool(hyde)
├─ Result 1: Shows older versions
├─ Agent: "Need recent info"
├─ Tool 2: web_search_tool()
├─ Result 2: Recent features
├─ Agent: "Complete picture"
├─ Iterations: 2-3
└─ Latency: ~5.2s
```

---

## State Evolution Comparison

```
ADAPTIVE RAG - Sequential State Updates

Initial State:
{
  query: "Compare Python and JavaScript",
  query_type: "",
  technique: "",
  confidence: 0.0,
  answer: "",
  sources: [],
  ...
}

After classify_query_node:
{
  query: "Compare Python and JavaScript",
  query_type: "complex",            ← Changed
  technique: "",
  confidence: 0.90,                  ← Set
  answer: "",
  sources: [],
  ...
}

After select_technique_node:
{
  query: "Compare Python and JavaScript",
  query_type: "complex",
  technique: "subquery",             ← Changed
  confidence: 0.90,
  answer: "",
  sources: [],
  ...
}

After execute_rag_node:
{
  query: "Compare Python and JavaScript",
  query_type: "complex",
  technique: "subquery",
  confidence: 0.90,
  answer: "Python is ...",           ← Changed
  sources: [{...}, {...}],           ← Changed
  ...
}

After build_response_node:
{
  query: "Compare Python and JavaScript",
  query_type: "complex",
  technique: "subquery",
  confidence: 0.90,
  answer: "Python is ...",
  sources: [{...}, {...}],
  execution_details: {               ← Added
    query_type: "complex",
    technique_selected: "subquery",
    routing_reason: "...",
  },
  ...
}


AGENTIC RAG - Message Accumulation

Initial State:
{
  messages: [
    HumanMessage("What's Python 3.13 latest features?")
  ],
  query: "What's Python 3.13 latest features?",
  answer: "",
  sources: [],
  ...
}

After agent_node (Iteration 1):
{
  messages: [
    HumanMessage("What's Python 3.13 latest features?"),
    AIMessage(content="...", tool_calls=[
      {tool: "internal_rag_tool", args: {technique: "hyde"}}
    ])
  ],                                 ← Message ADDED
  query: "What's Python 3.13 latest features?",
  answer: "",
  sources: [],
  ...
}

After tools execution:
{
  messages: [
    HumanMessage("What's Python 3.13 latest features?"),
    AIMessage(content="...", tool_calls=[...]),
    ToolMessage(content={              ← Message ADDED
      "answer": "Python 3.13 features...",
      "sources": [...],
      "technique_used": "hyde"
    })
  ],
  query: "What's Python 3.13 latest features?",
  answer: "",
  sources: [],
  ...
}

After agent_node (Iteration 2):
{
  messages: [
    HumanMessage("What's Python 3.13 latest features?"),
    AIMessage(content="...", tool_calls=[...]),
    ToolMessage(content={...}),
    AIMessage(content="...", tool_calls=[  ← Message ADDED
      {tool: "web_search_tool", args: {...}}
    ])
  ],
  query: "What's Python 3.13 latest features?",
  answer: "",
  sources: [],
  ...
}

After tools execution (web search):
{
  messages: [
    HumanMessage("What's Python 3.13 latest features?"),
    AIMessage(content="...", tool_calls=[...]),
    ToolMessage(content={...}),
    AIMessage(content="...", tool_calls=[...]),
    ToolMessage(content={              ← Message ADDED
      "answer": "Latest Python 3.13...",
      "sources": [...]
    })
  ],
  query: "What's Python 3.13 latest features?",
  answer: "",
  sources: [],
  ...
}

After agent_node (Iteration 3):
{
  messages: [                          ← All messages preserved
    HumanMessage(...),
    AIMessage(...),
    ToolMessage(...),
    AIMessage(...),
    ToolMessage(...),
    AIMessage(content="...", tool_calls=[])  ← No more tool calls
  ],
  query: "What's Python 3.13 latest features?",
  answer: "",                          ← Still empty
  sources: [],
  ...
}

After extract_final_answer:
{
  messages: [...],                     ← Unchanged
  query: "What's Python 3.13 latest features?",
  answer: "Python 3.13 has ...",       ← Extracted from messages
  sources: [{...}, {...}],             ← Extracted from last ToolMessage
  execution_details: {
    technique_used: "internal_rag_tool + web_search_tool",
    total_messages: 6,                 ← Number of messages
  },
  ...
}
```

---

## Loop Mechanisms

```
ADAPTIVE RAG - No Looping (Linear)

invoke(state)
  ├─ classify_query_node()
  │  └─ return updated_state
  ├─ select_technique_node()
  │  └─ return updated_state
  ├─ execute_rag_node()
  │  └─ return updated_state
  ├─ build_response_node()
  │  └─ return updated_state
  └─ END

Total calls: Always exactly 4 nodes
Result: Same every time for same query (deterministic)


AGENTIC RAG - Conditional Looping (Variable)

invoke(state, config={recursion_limit: 10})
  ├─ agent_node()
  │  └─ Check: tool_calls?
  ├─ should_continue() → "tools" or "end"
  │
  ├─ IF "tools":
  │  ├─ tools execution
  │  ├─ agent_node() again (LOOP!)
  │  ├─ should_continue() → "tools" or "end"
  │  └─ [Repeat until "end" or recursion_limit]
  │
  ├─ IF "end":
  │  └─ extract_final_answer()
  │
  └─ END

Total calls: 2 to 20+ node invocations (variable)
Result: Can vary based on agent decisions (stochastic)
```

---

## Error Handling Flows

```
ADAPTIVE RAG Error Handling

classify_query_node:
  try:
    response = llm.invoke(prompt)
    classification = parse_and_validate(response)
  except:
    classification = "simple"      ← Fallback (safe default)
    confidence = 0.5               ← Mark as low confidence

If classification validation fails:
  if classification not in VALID_CATEGORIES:
    for cat in VALID_CATEGORIES:
      if cat in classification:    ← Try substring match
        classification = cat
        break
    else:
      classification = "simple"    ← Fallback again

Result: Always produces valid output, but may use wrong technique


AGENTIC RAG Error Handling

agent_node:
  messages = state.get("messages", [])
  response = llm_with_tools.invoke(messages)
  └─ Binds tools → LLM understands tool schemas

should_continue:
  try:
    last_message = state["messages"][-1]
  except IndexError:
    return "end"                   ← Graceful fallback
  
  if last_message.tool_calls:
    return "tools"
  else:
    return "end"

If max_iterations reached:
  LangGraph stops execution
  extract_final_answer() gets current state
  └─ Returns best attempt so far

Result: Can handle partial failures, adapts gracefully
```

---

## Query Routing Decision Tree

```
ADAPTIVE RAG - Predetermined Routes

Query Input
  │
  ├─ Is query asking "What is X?" / "Qual é X?"
  │  └─ Classification: "simple"
  │     └─ Technique: baseline
  │        └─ Fast, direct retrieval
  │
  ├─ Does query have "Compare", "diferença", "vs"?
  │  └─ Classification: "complex"
  │     └─ Technique: subquery
  │        └─ Break into parts
  │
  ├─ Does query ask "How", "Why", "Explique"?
  │  └─ Classification: "abstract"
  │     └─ Technique: hyde
  │        └─ Hypothetical embeddings
  │
  └─ Is query about medical/legal/technical domain?
     └─ Classification: "precision"
        └─ Technique: reranking
           └─ Cross-encoder reranking

FIXED MAPPING: 4 categories → 4 techniques (1:1)


AGENTIC RAG - Dynamic Agent Decision Tree

Query Input
  │
  ├─ Agent analyzes:
  │  ├─ What is this query about?
  │  ├─ Do I have relevant tools?
  │  ├─ Which tool best fits?
  │  ├─ Should I search or answer directly?
  │  └─ If searching, which technique?
  │
  ├─ Agent decides:
  │  ├─ Need information? YES/NO
  │  ├─ Which tool? (RAG vs Web)
  │  ├─ Which technique? (baseline/hyde/reranking)
  │  └─ Execute and analyze results
  │
  ├─ Loop Decision:
  │  ├─ Did tool call succeed?
  │  ├─ Do I have enough info?
  │  ├─ Should I try different tool?
  │  ├─ Reached max iterations?
  │  └─ Ready to answer?
  │
  └─ Multiple possible paths:
     ├─ RAG only (1 iteration)
     ├─ RAG then Web (2 iterations)
     ├─ Web only (1 iteration)
     ├─ Direct answer (0 iterations)
     └─ Multiple RAG techniques (2+ iterations)

FLEXIBLE ROUTING: N-to-N mapping (dynamic)
```

---

## LLM Call Comparison

```
ADAPTIVE RAG - Fixed LLM Calls

Call 1: classify_query_node
├─ Purpose: Classify query
├─ Prompt: Classification prompt (50-100 tokens)
├─ Response: "simple" or "complex" or ... (5-10 tokens)
├─ Cost: ~$0.0001
├─ Always executed

Call 2: execute_rag_node → technique specific LLM
├─ Purpose: Generate answer (from technique)
├─ Prompt: RAG context + generation prompt (500-1000 tokens)
├─ Response: Full answer (200-500 tokens)
├─ Cost: ~$0.001
├─ Always executed

Total per query: ~2 LLM calls (classif + generation)
Total tokens: ~700-1500
Predictable cost


AGENTIC RAG - Variable LLM Calls

Call 1: agent_node (Iteration 1)
├─ Purpose: Agent reasoning
├─ Prompt: System prompt + messages history (500+ tokens)
├─ Response: Reasoning + tool_calls (200+ tokens)
├─ Always executed
├─ Cost: ~$0.0005

Call 2: agent_node (after tool result)
├─ Purpose: Analyze tool result
├─ Prompt: Updated messages (tool response added) (700+ tokens)
├─ Response: More reasoning ± tool_calls (200+ tokens)
├─ May execute (depends on should_continue)
├─ Cost: ~$0.0005

Call N: agent_node (Iteration N)
├─ Purpose: Refine or finalize
├─ Prompt: Full message history (1000+ tokens)
├─ Response: Final decision or more tools (200+ tokens)
├─ May execute (up to max_iterations)
├─ Cost: ~$0.0005 each

Total per query: ~2-10 LLM calls (variable)
Total tokens: ~1500-5000
Variable cost (2-5x Adaptive)
```

---

## Quick Reference: Which System Does What

```
┌─────────────────────┬─────────────────┬─────────────────────┐
│ Scenario            │ Adaptive RAG    │ Agentic RAG         │
├─────────────────────┼─────────────────┼─────────────────────┤
│ Simple query        │ baseline (fast) │ baseline (ok)       │
│ Complex query       │ subquery (good) │ Agentic (better)    │
│ Novel query type    │ May fail        │ Adapts              │
│ Outdated docs       │ Wrong answer    │ Try web search      │
│ Misclassification   │ Stuck           │ Can refine          │
│ Speed critical      │ Best           │ Too slow            │
│ Quality critical    │ Good           │ Best                │
│ Cost critical       │ Best           │ Too expensive       │
│ Predictability      │ Perfect        │ Variable            │
│ Flexibility         │ Limited        │ Excellent           │
└─────────────────────┴─────────────────┴─────────────────────┘
```

