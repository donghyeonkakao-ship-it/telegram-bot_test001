import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# RSS 피드 목록 (AI/실리콘밸리 매체)
AI_RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "VentureBeat": "https://venturebeat.com/feed/",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "Hacker News AI": "https://hnrss.org/newest?q=artificial+intelligence+LLM&count=10",
    "a16z": "https://a16z.com/feed/",
    "TLDR AI": "https://tldr.tech/ai/rss",
}

# RSS 피드 목록 (반도체/하드웨어 매체)
SEMI_RSS_FEEDS = {
    "Tom's Hardware": "https://www.tomshardware.com/feeds/all",
    "EE Times": "https://www.eetimes.com/feed/",
    "Hacker News Semi": "https://hnrss.org/newest?q=semiconductor+chip+TSMC&count=10",
    "SemiAnalysis": "https://www.semianalysis.com/feed",
}

NAVER_SEARCH_URL = "https://openapi.naver.com/v1/search/news.json"
NAVER_AI_QUERY = "AI 인공지능 LLM 생성형AI"
NAVER_SEMI_QUERY = "반도체 HBM TSMC 엔비디아 파운드리"

GEMINI_MODEL = "gemini-2.5-flash"
