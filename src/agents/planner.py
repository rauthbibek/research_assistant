"""
Planner agent — generates a structured research plan from the topic.
"""

from __future__ import annotations

import json
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_llm
from src.state import ResearchState


PLANNER_SYSTEM_PROMPT = """\
You are a senior research planner. Given a research topic and optionally a list \
of blog URLs, produce a **research plan** in JSON format.

Output ONLY valid JSON with this schema:
{{
  "sub_questions": ["question 1", "question 2", ...],
  "search_queries": ["query 1", "query 2", ...],
  "urls_to_scrape": ["url1", "url2", ...]
}}

Rules:
- Generate 3-5 focused sub-questions that, when answered, will provide \
  comprehensive coverage of the topic.
- Generate 3-5 web search queries optimised for finding high-quality sources.
- Include any blog URLs the user provided in `urls_to_scrape`.
- Keep queries specific and diverse (different angles on the topic).
"""


def planner_node(state: ResearchState) -> dict:
    """
    Generate or refine a research plan based on the topic and any
    previously collected data.
    """
    llm = get_llm(temperature=0.3, streaming=False)

    topic = state["topic"]
    blog_urls = state.get("blog_urls", [])
    iteration = state.get("iteration", 0)

    user_content = f"**Research Topic:** {topic}\n"

    if blog_urls:
        user_content += f"\n**Blog URLs to include:**\n"
        for url in blog_urls:
            user_content += f"- {url}\n"

    # On subsequent iterations, add context about what we already have
    if iteration > 0:
        existing_sources = state.get("sources", [])
        user_content += (
            f"\n**Note:** We already have {len(existing_sources)} sources collected. "
            f"Generate NEW, DIFFERENT search queries to fill gaps in our research. "
            f"Focus on angles not yet covered."
        )

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)

    # Parse JSON from the response
    try:
        content = response.content.strip()
        # Handle markdown code blocks
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        plan = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        plan = {
            "sub_questions": [f"What are the key aspects of {topic}?"],
            "search_queries": [topic],
            "urls_to_scrape": blog_urls,
        }

    # Ensure blog URLs are included
    existing_urls = set(plan.get("urls_to_scrape", []))
    for url in blog_urls:
        if url not in existing_urls:
            plan.setdefault("urls_to_scrape", []).append(url)

    return {
        "research_plan": plan,
        "iteration": iteration + 1,
        "messages": [f"📋 Research plan created (iteration {iteration + 1})"],
    }
