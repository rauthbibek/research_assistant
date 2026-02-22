"""
Configuration and LLM factory for the research assistant.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load .env from project root
load_dotenv()


def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    streaming: bool = True,
) -> ChatOpenAI:
    """
    Return a configured ChatOpenAI instance.

    Reads defaults from environment variables:
        LLM_MODEL       (default: gpt-4o-mini)
        LLM_TEMPERATURE (default: 0.2)
    """
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature = (
        temperature
        if temperature is not None
        else float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        streaming=streaming,
    )


# ── Constants ────────────────────────────────────────────────────────
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
MAX_SCRAPE_LENGTH = int(os.getenv("MAX_SCRAPE_LENGTH", "8000"))  # chars
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "2"))
