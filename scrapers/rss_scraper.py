import asyncio
import feedparser
import aiohttp
from config import AI_RSS_FEEDS, SEMI_RSS_FEEDS

_TIMEOUT = aiohttp.ClientTimeout(total=10)
_sem: asyncio.Semaphore | None = None


def _get_sem() -> asyncio.Semaphore:
    global _sem
    if _sem is None:
        _sem = asyncio.Semaphore(4)
    return _sem


def _parse_content(content: str, url: str, max_items: int) -> list[dict]:
    feed = feedparser.parse(content)
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
    async with _get_sem():
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, _parse_content, content, url, max_items)
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
