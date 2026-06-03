"""
RSS 피드를 주기적으로 폴링해 중요 속보를 감지합니다.

감지 기준: 제목에 고영향 키워드가 1개 이상 포함된 신규 기사
중복 방지: 이미 처리한 URL을 인메모리 셋으로 추적
워밍업: 봇 첫 실행 시 기존 기사를 already-seen으로 마킹하여 재발송 방지
"""
import asyncio
import logging

from config import AI_RSS_FEEDS, SEMI_RSS_FEEDS
from scrapers.rss_scraper import _fetch_feed

logger = logging.getLogger(__name__)

_seen_urls: set[str] = set()
_warmed_up: bool = False

# 이 중 하나라도 제목에 포함되면 속보로 판단
_BREAKING_KEYWORDS = [
    "acquir",        # acquires / acquisition / acquired
    "merger",
    " ipo ",
    "data breach",
    "cyberattack",
    "hacked",
    "bankrupt",
    "mass layoff",
    "layoffs",
    "shutdown",
    "sanctions",
    "export ban",
    "chip ban",
    "emergency",
    "$1 billion",
    "$2 billion",
    "$3 billion",
    "$5 billion",
    "$10 billion",
    "billion funding",
    "billion deal",
    "인수",
    "합병",
    "파산",
    "대규모 해고",
    "수출 규제",
    "긴급",
]


def _is_breaking(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in _BREAKING_KEYWORDS)


async def _fetch_all() -> list[dict]:
    all_feeds = {**AI_RSS_FEEDS, **SEMI_RSS_FEEDS}
    tasks = [_fetch_feed(url, 10) for url in all_feeds.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    articles = []
    for r in results:
        if isinstance(r, list):
            articles.extend(r)
    return articles


async def warmup() -> None:
    """봇 시작 시 현재 기사들을 seen으로 등록 (발송 없음)."""
    global _warmed_up
    articles = await _fetch_all()
    for a in articles:
        _seen_urls.add(a.get("link", ""))
    _warmed_up = True
    logger.info("breaking_detector warmup: %d URLs marked as seen", len(_seen_urls))


async def detect_breaking_news() -> list[dict]:
    """새로운 속보 기사 목록을 반환합니다."""
    global _warmed_up
    articles = await _fetch_all()

    if not _warmed_up:
        for a in articles:
            _seen_urls.add(a.get("link", ""))
        _warmed_up = True
        return []

    breaking = []
    for a in articles:
        url = a.get("link", "")
        if url in _seen_urls:
            continue
        _seen_urls.add(url)
        if _is_breaking(a.get("title", "")):
            breaking.append(a)

    return breaking
