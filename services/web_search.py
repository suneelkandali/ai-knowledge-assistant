"""
Web search tool using DuckDuckGo — free, no API key required.
"""

import json
from typing import Optional

from duckduckgo_search import DDGS


def search_web(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
) -> list[dict[str, str]]:
    """
    Search the web using DuckDuckGo and return a list of results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
        region: Region code (default: "wt-wt" for worldwide).

    Returns:
        A list of dicts with keys: title, url, snippet.

    Raises:
        RuntimeError: If the search request fails.
    """
    if not query or not query.strip():
        return []

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    keywords=query.strip(),
                    region=region,
                    max_results=max_results,
                )
            )

        formatted = []
        for r in results:
            formatted.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
            )

        return formatted

    except Exception as exc:
        raise RuntimeError(
            f"The web search request failed. "
            f"Ensure you have internet connectivity. "
            f"Original error: {exc}"
        ) from exc


def format_search_results(results: list[dict[str, str]]) -> str:
    """
    Format search results into a readable text block for LLM context.

    Args:
        results: The list of search result dicts from search_web().

    Returns:
        A formatted string with numbered entries.
    """
    if not results:
        return "No search results found."

    sections = []
    for index, item in enumerate(results, start=1):
        sections.append(
            f"[{index}] {item['title']}\n"
            f"    URL: {item['url']}\n"
            f"    {item['snippet']}"
        )

    return "\n\n".join(sections)


def build_web_search_context(query: str, max_results: int = 5) -> str:
    """
    Convenience function: search the web and return a ready-to-use context string.

    Args:
        query: The search query.
        max_results: Maximum results to fetch.

    Returns:
        A formatted context string prefixed with a source label,
        or an empty string if the search fails.
    """
    try:
        results = search_web(query, max_results=max_results)
        if not results:
            return ""
        formatted = format_search_results(results)
        return (
            "The following information was retrieved from the web. "
            "Use it to supplement your knowledge, especially for "
            "current events or recent developments.\n\n"
            f"{formatted}"
        )
    except RuntimeError:
        return ""


if __name__ == "__main__":
    # Quick test
    results = search_web("Python programming language 2025", max_results=3)
    print("=== Raw Results ===")
    print(json.dumps(results, indent=2))
    print("\n=== Formatted Context ===")
    print(build_web_search_context("latest AI news", max_results=3))
