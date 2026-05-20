import logging
from telegram import Update
from telegram.ext import ContextTypes
from scrapers.rss_scraper import fetch_ai_rss
from scrapers.naver_scraper import fetch_naver_news
from services.gemini_service import summarize_ai_news
from utils.formatter import ai_report
from config import NAVER_AI_QUERY

logger = logging.getLogger(__name__)


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("🔄 AI 브리핑 리포트 생성 중입니다…")

    try:
        rss = await fetch_ai_rss()
        naver = await fetch_naver_news(NAVER_AI_QUERY)
        articles = rss + naver

        if not articles:
            await msg.edit_text("⚠️ 현재 수집된 기사가 없습니다. 잠시 후 다시 시도해주세요.")
            return

        summary = await summarize_ai_news(articles)
        report = ai_report(summary, articles)
        await msg.edit_text(report, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        logger.error("ai_command error: %s", e)
        await msg.edit_text("⚠️ 리포트 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
