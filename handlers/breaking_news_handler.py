"""
자동 속보 감지 핸들러.
JobQueue에서 10분마다 호출되며, 감지된 속보를 채널에 즉시 발송합니다.
"""
import logging

from telegram.ext import ContextTypes

from config import TELEGRAM_CHANNEL_ID
from services.breaking_detector import detect_breaking_news
from services.gemini_service import summarize_breaking_article
from utils.formatter import breaking_news_auto

logger = logging.getLogger(__name__)


async def auto_breaking_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not TELEGRAM_CHANNEL_ID:
        logger.warning("TELEGRAM_CHANNEL_ID가 설정되지 않아 속보 발송을 건너뜁니다.")
        return

    try:
        articles = await detect_breaking_news()
    except Exception as e:
        logger.error("breaking_detector error: %s", e)
        return

    for article in articles:
        try:
            sections = await summarize_breaking_article(
                title=article["title"],
                source=article["source"],
            )
            summary = sections.get("SUMMARY", article["title"])
            impact = sections.get("IMPACT", "—")
            message = breaking_news_auto(
                title=article["title"],
                summary=summary,
                impact=impact,
                source=article["source"],
                link=article.get("link", ""),
            )
            await context.bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            logger.info("속보 발송: %s", article["title"])
        except Exception as e:
            logger.error("속보 발송 실패 (%s): %s", article.get("title", ""), e)
