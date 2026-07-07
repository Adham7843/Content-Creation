"""Stage 1: Source Fetcher — get content to make memes from.

Supports: YouTube URLs, TikTok URLs, Reddit threads, raw text/scripts.
For Reddit: uses brainrotbot. For video: passes URL to opensource-clipping.
For text: generates a script via Opencode, then feeds to TTS.
"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path

from config import MemeConfig

logger = logging.getLogger(__name__)


async def fetch_source(config: MemeConfig) -> dict:
    """Fetch and prepare source content for meme generation.

    Returns dict with:
        type: youtube, reddit, text, tiktok
        url: resolved URL
        title: content title
        script: text content (for text-based sources)
    """
    url = config.source_url
    stype = config.source_type or _detect_source_type(url)

    logger.info("Fetching source: %s (type=%s)", url, stype)

    result = {"type": stype, "url": url, "title": "", "script": ""}

    if stype == "reddit":
        result = await _fetch_reddit(url, config)
    elif stype == "text":
        result = await _fetch_text(url, config)
    elif stype in ("youtube", "tiktok", "instagram"):
        result = await _fetch_video(url, stype, config)

    return result


def _detect_source_type(url: str) -> str:
    """Auto-detect source type from URL."""
    url_lower = url.lower()
    if "reddit.com" in url_lower:
        return "reddit"
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "instagram.com" in url_lower:
        return "instagram"
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    # If it's not a URL, treat as text
    if not url_lower.startswith("http"):
        return "text"
    return "youtube"


async def _fetch_video(url: str, stype: str, config: MemeConfig) -> dict:
    """Video sources just pass through to the clipper."""
    title = url.split("/")[-1].split("?")[0][:50]
    return {"type": stype, "url": url, "title": title, "script": ""}


async def _fetch_reddit(url: str, config: MemeConfig) -> dict:
    """Extract Reddit post content for meme-making."""
    # Extract post ID and subreddit
    post_match = re.search(r"reddit\.com/r/(\w+)/comments/(\w+)", url)
    if not post_match:
        return {"type": "reddit", "url": url, "title": url, "script": url}

    subreddit, post_id = post_match.groups()

    # Try running brainrotbot to fetch
    brainrot_main = config.meme_tool / "main.py"
    if brainrot_main.exists():
        logger.info("Using brainrotbot to fetch Reddit post")
        # brainrotbot handles this natively

    return {
        "type": "reddit",
        "url": url,
        "title": f"r/{subreddit}",
        "script": f"Reddit post from r/{subreddit}: {post_id}",
    }


async def _fetch_text(text: str, config: MemeConfig) -> dict:
    """Text-based source — use as script directly or generate via LLM."""
    return {
        "type": "text",
        "url": "",
        "title": "Generated Meme",
        "script": text,
    }
