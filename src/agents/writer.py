"""
Writer agent — produces the final markdown research report.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_llm
from src.state import ResearchState


WRITER_SYSTEM_PROMPT = """\
You are an expert research report writer. Using the provided analysis, \
produce a polished, comprehensive research report in **Markdown format**.

## Report Structure:
1. **Title** — Clear, descriptive title for the research
2. **Executive Summary** — 2-3 paragraph overview of key findings
3. **Introduction** — Background context and scope of research
4. **Key Findings** — Main discoveries organized by theme (use ### subheadings)
5. **Detailed Analysis** — In-depth discussion with evidence and citations
6. **Conclusions** — Synthesis of findings and their implications
7. **References** — Numbered list of all sources used

## Guidelines:
- Write in a professional, objective tone
- Use bullet points and tables where appropriate for clarity
- Include inline citations like [1], [2] that map to the References section
- Highlight particularly important findings with **bold text**
- Keep the report focused and well-organized (1500-3000 words)
"""


def writer_node(state: ResearchState) -> dict:
    """
    Generate the final research report from the analysis.
    """
    llm = get_llm(temperature=0.3, streaming=False)

    topic = state["topic"]
    analysis = state.get("analysis", "")
    sources = state.get("sources", [])

    # Build reference list
    references = ""
    for i, source in enumerate(sources, 1):
        title = source.get("title", "Untitled")
        url = source.get("url", "N/A")
        references += f"[{i}] {title} — {url}\n"

    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"**Research Topic:** {topic}\n\n"
            f"## Analysis to Base Report On:\n{analysis}\n\n"
            f"## Available References:\n{references}\n\n"
            f"Write the complete research report now."
        )),
    ]

    response = llm.invoke(messages)

    return {
        "report": response.content,
        "messages": [f"📝 Research report generated ({len(response.content)} chars)"],
    }
