"""
Agentic RAG - Orchestrator (LangGraph)

Gerencia o workflow do agente:
- AgentState: Estado mantido durante execução
- Nodes: agent_node, should_continue, extract_final_answer
- Graph: StateGraph com ReAct loop
"""

import json
from typing import Dict, Any, List, Literal, Annotated
from typing_extensions import TypedDict
from operator import add

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Imports internos
from .tools import AGENTIC_TOOLS
from .prompts import get_system_prompt

# Imports relativos ou absolutos dependendo do contexto
try:
    from ...core.llm import get_llm
except ImportError:
    from core.llm import get_llm


# ============================================
# Estado do Agente
# ============================================

class AgentState(TypedDict):
    """Estado mantido durante execução do agente"""
    messages: Annotated[List[BaseMessage], add]
    query: str
    answer: str
    sources: List[Dict]
    metrics: Dict[str, Any]
    execution_details: Dict[str, Any]


# ============================================
# Nós do Grafo
# ============================================

def agent_node(state: AgentState) -> AgentState:
    """
    Nó principal: Agent decide qual ferramenta usar.

    ReAct Pattern:
    - Reasoning: Analisa a query
    - Acting: Decide qual tool chamar
    """
    llm = get_llm()

    # Bind tools ao LLM
    llm_with_tools = llm.bind_tools(AGENTIC_TOOLS)

    # Agent raciocina e decide
    messages = state.get("messages", [])

    if not messages:
        raise ValueError("Estado sem mensagens!")

    response = llm_with_tools.invoke(messages)

    # Atualiza estado - append simples
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Decide se agent deve continuar (chamar tool) ou terminar.
    """
    last_message = state["messages"][-1]

    # Se agent chamou tool → executa tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Senão → termina
    return "end"


def extract_final_answer(state: AgentState) -> AgentState:
    """
    Extrai resposta final e metrics do estado.
    """
    messages = state["messages"]

    # Procura última ToolMessage (resultado do RAG)
    tool_results = [msg for msg in messages if isinstance(msg, ToolMessage)]

    if tool_results:
        # ToolMessage.content pode ser str ou já dict
        content = tool_results[-1].content

        if isinstance(content, str):
            try:
                last_result = json.loads(content)
            except json.JSONDecodeError:
                # Se não é JSON, assume resposta direta
                return {
                    **state,
                    "answer": content,
                    "sources": [],
                    "metrics": {},
                    "execution_details": {
                        "technique_used": "unknown",
                        "total_messages": len(messages),
                    },
                }
        else:
            last_result = content

        return {
            **state,
            "answer": last_result.get("answer", ""),
            "sources": last_result.get("sources", []),
            "metrics": last_result.get("metrics", {}),
            "execution_details": {
                "technique_used": last_result.get("technique_used", "unknown"),
                "total_messages": len(messages),
            },
        }

    # Se não tem tool result, usa última mensagem do agent
    last_ai_msg = [msg for msg in messages if isinstance(msg, AIMessage)][-1]

    return {
        **state,
        "answer": last_ai_msg.content,
        "sources": [],
        "metrics": {},
        "execution_details": {
            "technique_used": "direct_answer",
            "total_messages": len(messages),
        },
    }


# ============================================
# Construção do Grafo
# ============================================

def create_agent_graph():
    """
    Cria StateGraph do agente.

    Flow:
    START → agent → should_continue
              ↓           ↓
            tools ←──────┘
              ↓
            agent → should_continue → END
    """
    workflow = StateGraph(AgentState)

    # Adiciona nós
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(AGENTIC_TOOLS))
    workflow.add_node("extract", extract_final_answer)

    # Define entry point
    workflow.set_entry_point("agent")

    # Define edges condicionais
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": "extract",
        },
    )

    # Tool sempre volta pro agent (ReAct loop)
    workflow.add_edge("tools", "agent")

    # Extract termina
    workflow.add_edge("extract", END)

    return workflow.compile()


# ============================================
# Funções Auxiliares
# ============================================

def create_initial_state(query: str, params: Dict[str, Any] = None) -> AgentState:
    """
    Cria estado inicial do agente.

    Args:
        query: Pergunta do usuário
        params: Parâmetros opcionais

    Returns:
        Estado inicial formatado
    """
    params = params or {}
    system_prompt = get_system_prompt(params)

    return {
        "messages": [
            HumanMessage(content=f"{system_prompt}\n\nPergunta: {query}")
        ],
        "query": query,
        "answer": "",
        "sources": [],
        "metrics": {},
        "execution_details": {},
    }
