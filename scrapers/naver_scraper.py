import re
import aiohttp
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NAVER_SEARCH_URL


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


async def fetch_naver_news(query: str, display: int = 7) -> list[dict]:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "sort": "date"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                NAVER_SEARCH_URL, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return [
                    {
                        "title": _strip_html(item.get("title", "")),
                        "link": item.get("originallink") or item.get("link", ""),
                        "source": "네이버 뉴스",
                    }
                    for item in data.get("items", [])
                    if item.get("title")
                ]
    except Exception:
        return []
