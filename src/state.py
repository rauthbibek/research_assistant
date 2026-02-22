"""
Shared state schema for the LangGraph research assistant workflow.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict


class SourceDocument(TypedDict, total=False):
    """A single source document collected during research."""
    url: str
    title: str
    content: str
    snippet: str
    source_type: str  # "web_search" | "blog" | "manual"
    word_count: int


class ResearchPlan(TypedDict, total=False):
    """Generated research plan."""
    sub_questions: list[str]
    search_queries: list[str]
    urls_to_scrape: list[str]


class ResearchState(TypedDict, total=False):
    """
    Central state for the research assistant graph.

    Fields using `Annotated[..., operator.add]` are append-only lists —
    each node can return new items and they'll be merged automatically.
    """

    # ── User inputs ───────────────────────────────────────────────
    topic: str
    blog_urls: list[str]

    # ── Planning ──────────────────────────────────────────────────
    research_plan: ResearchPlan

    # ── Data collection ───────────────────────────────────────────
    sources: Annotated[list[SourceDocument], operator.add]

    # ── Analysis & output ─────────────────────────────────────────
    analysis: str
    report: str

    # ── Control flow ──────────────────────────────────────────────
    iteration: int          # current research loop iteration
    max_iterations: int     # max allowed iterations (default 2)
    enough_data: bool       # set by researcher when data is sufficient

    # ── Logging ───────────────────────────────────────────────────
    errors: Annotated[list[str], operator.add]
    messages: Annotated[list[str], operator.add]
