"""
Analyzer agent — synthesizes collected research into structured analysis.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_llm
from src.state import ResearchState


ANALYZER_SYSTEM_PROMPT = """\
You are a senior research analyst. You will receive raw data collected from \
multiple web sources and blog posts about a specific topic. Your job is to:

1. **Identify key themes** and recurring patterns across sources.
2. **Extract critical findings** — facts, statistics, expert opinions.
3. **Note contradictions** or areas of disagreement between sources.
4. **Assess source quality** and reliability.
5. **Identify knowledge gaps** that remain.

Produce a structured analysis using clear markdown headings. Cite sources \
by their URL when referencing specific information.
"""


def analyzer_node(state: ResearchState) -> dict:
    """
    Analyze all collected sources and produce a structured analysis.
    """
    llm = get_llm(temperature=0.2, streaming=False)

    topic = state["topic"]
    sources = state.get("sources", [])

    # Build source summaries for the prompt
    source_text = ""
    for i, source in enumerate(sources, 1):
        title = source.get("title", "Untitled")
        url = source.get("url", "N/A")
        content = source.get("content", source.get("snippet", ""))
        source_type = source.get("source_type", "unknown")

        source_text += (
            f"\n### Source {i} [{source_type}]\n"
            f"**Title:** {title}\n"
            f"**URL:** {url}\n"
            f"**Content:**\n{content[:3000]}\n"
            f"---\n"
        )

    if not source_text:
        return {
            "analysis": "No sources were collected. Unable to perform analysis.",
            "messages": ["⚠️ Analysis skipped — no sources available"],
        }

    messages = [
        SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"**Research Topic:** {topic}\n\n"
            f"**Number of Sources:** {len(sources)}\n\n"
            f"## Collected Sources\n{source_text}\n\n"
            f"Provide a comprehensive analysis of the above sources."
        )),
    ]

    response = llm.invoke(messages)

    return {
        "analysis": response.content,
        "messages": [f"🔬 Analysis complete — synthesized {len(sources)} sources"],
    }
