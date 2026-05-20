import asyncio
import feedparser
from config import AI_RSS_FEEDS, SEMI_RSS_FEEDS


def _parse_feed(url: str, max_items: int) -> list[dict]:
    feed = feedparser.parse(url)
    source = feed.feed.get("title", url)
    return [
        {
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", ""),
            "source": source,
        }
        for entry in feed.entries[:max_items]
        if entry.get("title") and entry.get("link")
    ]


async def _fetch_feed(url: str, max_items: int = 5) -> list[dict]:
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, _parse_feed, url, max_items)
    except Exception:
        return []


async def fetch_ai_rss() -> list[dict]:
    tasks = [_fetch_feed(url, 4) for url in AI_RSS_FEEDS.values()]
    results = await asyncio.gather(*tasks)
    articles = [item for batch in results for item in batch]
    return articles[:20]


async def fetch_semi_rss() -> list[dict]:
    tasks = [_fetch_feed(url, 5) for url in SEMI_RSS_FEEDS.values()]
    results = await asyncio.gather(*tasks)
    articles = [item for batch in results for item in batch]
    return articles[:20]
