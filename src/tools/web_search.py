"""
Web search tool — uses Tavily when available, falls back to DuckDuckGo.
"""

from __future__ import annotations

import os
from langchain_core.tools import tool


def _search_tavily(query: str, max_results: int) -> list[dict]:
    """Search using Tavily API."""
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(query=query, max_results=max_results)
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "source_type": "web_search",
        }
        for r in response.get("results", [])
    ]


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    """Fallback search using DuckDuckGo."""
    from duckduckgo_search import DDGS

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
            "source_type": "web_search",
        }
        for r in results
    ]


@tool
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for information on a given query.
    Returns a list of results with title, url, and snippet.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).
    """
    try:
        if os.getenv("TAVILY_API_KEY"):
            return _search_tavily(query, max_results)
        else:
            return _search_duckduckgo(query, max_results)
    except Exception as e:
        return [{"error": str(e), "source_type": "web_search"}]
