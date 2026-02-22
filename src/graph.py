"""
LangGraph workflow — wires together planner → researcher → analyzer → writer
with conditional looping for iterative research.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from src.state import ResearchState
from src.config import MAX_ITERATIONS
from src.agents.planner import planner_node
from src.agents.researcher import researcher_node
from src.agents.analyzer import analyzer_node
from src.agents.writer import writer_node


def _should_continue_research(state: ResearchState) -> str:
    """
    Conditional edge after the researcher node.
    If we don't have enough data AND haven't hit the iteration limit,
    loop back to the planner for refined queries.
    """
    enough_data = state.get("enough_data", False)
    iteration = state.get("iteration", 1)
    max_iter = state.get("max_iterations", MAX_ITERATIONS)

    if enough_data or iteration >= max_iter:
        return "analyzer"
    else:
        return "planner"


def build_graph() -> StateGraph:
    """
    Construct and compile the research assistant graph.

    Flow:
        START → planner → researcher →[conditional]→ analyzer → writer → END
                   ↑                       |
                   └───── (loop if not enough data)
    """
    graph = StateGraph(ResearchState)

    # ── Add nodes ────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("writer", writer_node)

    # ── Add edges ────────────────────────────────────────────────
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")

    # Conditional: loop back to planner or proceed to analyzer
    graph.add_conditional_edges(
        "researcher",
        _should_continue_research,
        {
            "planner": "planner",
            "analyzer": "analyzer",
        },
    )

    graph.add_edge("analyzer", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


def run_research(topic: str, blog_urls: list[str] | None = None) -> ResearchState:
    """
    High-level helper — run the full research pipeline and return final state.

    Args:
        topic: The research topic.
        blog_urls: Optional list of blog URLs to include.

    Returns:
        The final ResearchState with the completed report.
    """
    app = build_graph()

    initial_state: ResearchState = {
        "topic": topic,
        "blog_urls": blog_urls or [],
        "sources": [],
        "errors": [],
        "messages": [],
        "iteration": 0,
        "max_iterations": MAX_ITERATIONS,
        "enough_data": False,
        "analysis": "",
        "report": "",
    }

    final_state = app.invoke(initial_state)
    return final_state
