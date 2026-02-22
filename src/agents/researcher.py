"""
Researcher agent — executes the research plan by searching and scraping.
"""

from __future__ import annotations

from src.state import ResearchState
from src.tools.web_search import web_search
from src.tools.blog_scraper import scrape_blog
from src.tools.summarizer import summarize_content


def researcher_node(state: ResearchState) -> dict:
    """
    Execute the research plan:
    1. Run all search queries from the plan
    2. Scrape all blog / URLs from the plan
    3. Summarize collected content
    """
    plan = state.get("research_plan", {})
    topic = state["topic"]

    collected_sources = []
    errors = []
    messages = []

    # ── 1. Web searches ──────────────────────────────────────────
    search_queries = plan.get("search_queries", [])
    messages.append(f"🔍 Running {len(search_queries)} web searches...")

    for query in search_queries:
        try:
            results = web_search.invoke({"query": query, "max_results": 5})
            if isinstance(results, list):
                for r in results:
                    if "error" not in r:
                        collected_sources.append({
                            "url": r.get("url", ""),
                            "title": r.get("title", ""),
                            "content": r.get("snippet", ""),
                            "snippet": r.get("snippet", ""),
                            "source_type": "web_search",
                            "word_count": len(r.get("snippet", "").split()),
                        })
                    else:
                        errors.append(f"Search error for '{query}': {r['error']}")
        except Exception as e:
            errors.append(f"Search failed for '{query}': {e}")

    # ── 2. Blog / URL scraping ───────────────────────────────────
    urls_to_scrape = plan.get("urls_to_scrape", [])
    messages.append(f"📄 Scraping {len(urls_to_scrape)} URLs...")

    for url in urls_to_scrape:
        try:
            result = scrape_blog.invoke({"url": url})
            if isinstance(result, dict) and "error" not in result:
                # Summarize long blog content for the research context
                content = result.get("content", "")
                if len(content) > 2000:
                    summary = summarize_content.invoke({
                        "text": content,
                        "focus": topic,
                    })
                    result["content"] = summary
                    result["word_count"] = len(summary.split())

                collected_sources.append(result)
            elif isinstance(result, dict):
                errors.append(f"Scrape error for {url}: {result.get('error', 'Unknown')}")
        except Exception as e:
            errors.append(f"Scrape failed for {url}: {e}")

    # ── 3. Determine if we have enough data ──────────────────────
    total_sources = len(state.get("sources", [])) + len(collected_sources)
    enough_data = total_sources >= 3  # at least 3 sources

    messages.append(
        f"✅ Collected {len(collected_sources)} new sources "
        f"({total_sources} total). Enough data: {enough_data}"
    )

    return {
        "sources": collected_sources,
        "enough_data": enough_data,
        "errors": errors,
        "messages": messages,
    }
