"""
Content summarizer tool — uses the LLM to produce focused summaries.
"""

from __future__ import annotations

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_llm


@tool
def summarize_content(text: str, focus: str) -> str:
    """
    Summarize a block of text, focusing on aspects relevant to the research topic.

    Args:
        text: The raw text content to summarize.
        focus: The research topic or focus area for the summary.
    """
    if not text or not text.strip():
        return "No content to summarize."

    llm = get_llm(temperature=0.1, streaming=False)

    messages = [
        SystemMessage(content=(
            "You are a precise research summarizer. Extract the key information "
            "from the provided text that is most relevant to the given research focus. "
            "Be concise but thorough. Include specific facts, data points, and insights. "
            "Preserve any important quotes or statistics."
        )),
        HumanMessage(content=(
            f"**Research Focus:** {focus}\n\n"
            f"**Text to Summarize:**\n{text[:6000]}\n\n"
            "Provide a focused summary (200-400 words):"
        )),
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Summarization failed: {e}"
