import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from scrapers.rss_scraper import fetch_ai_rss, fetch_semi_rss
from scrapers.naver_scraper import fetch_naver_news
from services.gemini_service import summarize_digest
from services.job_store import set_job, remove_job, job_name
from utils.formatter import digest_report
from config import NAVER_AI_QUERY, NAVER_SEMI_QUERY

logger = logging.getLogger(__name__)

# interval_key → (시간, 라벨)
INTERVAL_MAP = {
    "3h": (3, "3시간"),
    "6h": (6, "6시간"),
    "12h": (12, "12시간"),
    "24h": (24, "24시간"),
}


def _make_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏰ 3시간", callback_data="notif_3h"),
            InlineKeyboardButton("⏰ 6시간", callback_data="notif_6h"),
        ],
        [
            InlineKeyboardButton("⏰ 12시간", callback_data="notif_12h"),
            InlineKeyboardButton("📅 24시간", callback_data="notif_24h"),
        ],
        [InlineKeyboardButton("🔕 알림 끄기", callback_data="notif_off")],
    ])


async def notification_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "⚙️ <b>정기 알림 주기 설정</b>\n\n"
        "AI + 반도체 뉴스 다이제스트를 얼마나 자주 받으시겠어요?",
        parse_mode="HTML",
        reply_markup=_make_keyboard(),
    )


async def notification_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    data = query.data  # "notif_3h" | "notif_off"

    # 기존 job 제거
    for job in context.job_queue.get_jobs_by_name(job_name(chat_id)):
        job.schedule_removal()

    if data == "notif_off":
        remove_job(chat_id)
        await query.edit_message_text(
            "🔕 <b>알림이 비활성화되었습니다.</b>\n"
            "다시 설정하려면 /notification 을 입력하세요.",
            parse_mode="HTML",
        )
        return

    key = data.removeprefix("notif_")
    interval_hours, label = INTERVAL_MAP[key]

    set_job(chat_id, interval_hours)
    context.job_queue.run_repeating(
        callback=_digest_job,
        interval=interval_hours * 3600,
        first=10,
        chat_id=chat_id,
        name=job_name(chat_id),
        data=chat_id,
    )

    await query.edit_message_text(
        f"✅ <b>알림 설정 완료!</b>\n\n"
        f"📬 매 <b>{label}</b>마다 AI + 반도체 뉴스 다이제스트를 전송합니다.\n\n"
        f"<i>알림을 변경하거나 끄려면 /notification 을 다시 입력하세요.</i>",
        parse_mode="HTML",
    )


async def _digest_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    try:
        ai_rss, semi_rss, naver_ai, naver_semi = await _gather_all()
        ai_articles = ai_rss + naver_ai
        semi_articles = semi_rss + naver_semi

        ai_summary, semi_summary = await summarize_digest(ai_articles, semi_articles)
        report = digest_report(ai_summary, semi_summary)

        await context.bot.send_message(
            chat_id=chat_id,
            text=report,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error("digest_job error for chat %s: %s", chat_id, e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ 다이제스트 생성 중 일시적 오류가 발생했습니다.",
        )


async def _gather_all():
    import asyncio
    return await asyncio.gather(
        fetch_ai_rss(),
        fetch_semi_rss(),
        fetch_naver_news(NAVER_AI_QUERY),
        fetch_naver_news(NAVER_SEMI_QUERY),
    )
