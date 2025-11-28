"""
RAG Analyst - Orchestrator Module

LangGraph-based agent orchestration for intelligent RAG analysis.
Creates and manages the agent workflow graph.

Flow: Question → Agent → Tools → Database → Analysis → Response
"""

from typing import TypedDict, Annotated, Sequence, Literal, Any, Optional
import operator
import asyncio

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config import settings
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS


# ============================================
# State Definition
# ============================================
class AnalystState(TypedDict):
    """State that flows through the analyst agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    tool_calls_made: list
    iterations: int


# ============================================
# Graph Nodes
# ============================================
def create_agent_node(llm):
    """Create the main agent node that processes messages."""

    def agent_node(state: AnalystState) -> dict:
        """Process messages and decide on tool use or final response."""
        messages = state["messages"]

        # Add system prompt if not present
        if not any(isinstance(m, dict) and m.get("role") == "system" for m in messages):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(messages)

        response = llm.invoke(messages)
        return {"messages": [response]}

    return agent_node


def should_continue(state: AnalystState) -> Literal["tools", "end"]:
    """Determine if we should continue to tools or end."""
    last_message = state["messages"][-1]

    # If the LLM wants to use tools, route to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end the conversation
    return "end"


# ============================================
# Graph Construction
# ============================================
def create_analyst_graph() -> StateGraph:
    """
    Create the RAG Analyst LangGraph agent.

    Graph Structure:
        START → agent ⟷ tools → END
                  ↓
                 END (when no more tools needed)
    """
    # Initialize LLM with tools
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
        max_output_tokens=4096,
    ).bind_tools(TOOLS)

    # Create tool node
    tool_node = ToolNode(TOOLS)

    # Build the graph
    workflow = StateGraph(AnalystState)

    # Add nodes
    workflow.add_node("agent", create_agent_node(llm))
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )

    # Tools always return to agent
    workflow.add_edge("tools", "agent")

    # Compile the graph
    return workflow.compile()


# ============================================
# Main Execution Function
# ============================================
async def run_analyst(question: str, max_iterations: int = 10) -> dict:
    """
    Run the RAG Analyst agent with a question.

    Args:
        question: User's question about RAG performance
        max_iterations: Maximum tool call iterations (safety limit)

    Returns:
        Dict with:
        - response: Final analysis text
        - tool_calls: List of tools used with result previews
        - iterations: Number of tool call iterations
    """
    agent = create_analyst_graph()

    initial_state = {
        "messages": [HumanMessage(content=question)],
        "tool_calls_made": [],
        "iterations": 0,
    }

    # Track tool calls
    tool_calls_made = []

    def run_sync():
        nonlocal tool_calls_made
        final_state = None

        for i, state in enumerate(agent.stream(initial_state)):
            if i >= max_iterations:
                break

            # Track tool calls
            for node_name, node_state in state.items():
                if node_name == "tools" and "messages" in node_state:
                    for msg in node_state["messages"]:
                        if isinstance(msg, ToolMessage):
                            tool_calls_made.append({
                                "tool": msg.name,
                                "result_preview": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                            })

            final_state = state

        return final_state

    final_state = await asyncio.to_thread(run_sync)

    # Extract final response
    final_response = ""
    if final_state:
        for node_state in final_state.values():
            if "messages" in node_state:
                for msg in node_state["messages"]:
                    if isinstance(msg, AIMessage) and msg.content:
                        final_response = msg.content

    return {
        "response": final_response,
        "tool_calls": tool_calls_made,
        "iterations": len(tool_calls_made),
    }
