"""
Blog / URL scraper tool — extracts main content from web pages.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

from src.config import MAX_SCRAPE_LENGTH


def _extract_main_content(soup: BeautifulSoup) -> str:
    """
    Heuristically extract the main text content from a parsed page.
    Tries <article>, <main>, then falls back to <body>.
    """
    # Remove noise elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try semantic containers first
    for selector in ["article", "main", '[role="main"]', ".post-content", ".entry-content"]:
        container = soup.select_one(selector)
        if container:
            return container.get_text(separator="\n", strip=True)

    # Fallback to body
    body = soup.find("body")
    if body:
        return body.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)


@tool
def scrape_blog(url: str) -> dict:
    """
    Scrape content from a blog post or web page URL.
    Returns the title, URL, extracted text content, and word count.

    Args:
        url: The full URL of the blog post or web page to scrape.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        content = _extract_main_content(soup)

        # Truncate to avoid blowing up context windows
        if len(content) > MAX_SCRAPE_LENGTH:
            content = content[:MAX_SCRAPE_LENGTH] + "\n\n[... content truncated ...]"

        word_count = len(content.split())

        return {
            "url": url,
            "title": title,
            "content": content,
            "word_count": word_count,
            "source_type": "blog",
        }

    except requests.exceptions.Timeout:
        return {"url": url, "error": "Request timed out", "source_type": "blog"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"Failed to fetch: {e}", "source_type": "blog"}
    except Exception as e:
        return {"url": url, "error": f"Parsing error: {e}", "source_type": "blog"}
