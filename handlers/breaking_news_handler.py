"""
긴급 속보 핸들러.
관리자가 /breaking <제목> | <기능 요약> | <시장 영향> 형식으로 입력하면
채널에 속보 포맷으로 즉시 발송합니다.

사용 예:
  /breaking 오픈AI GPT-5 출시 | 추론 능력 30% 향상, 멀티모달 강화 | 구글·앤트로픽 경쟁 압박 심화
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.formatter import breaking_news
from config import TELEGRAM_CHANNEL_ID

logger = logging.getLogger(__name__)


async def breaking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args) if context.args else ""
    parts = [p.strip() for p in raw.split("|")]

    if len(parts) < 3:
        await update.message.reply_text(
            "⚠️ 형식을 맞춰주세요:\n"
            "<code>/breaking 제목 | 기능 요약 | 시장 영향</code>",
            parse_mode="HTML",
        )
        return

    title, features, impact = parts[0], parts[1], parts[2]
    message = breaking_news(title, features, impact)

    try:
        await context.bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode="HTML",
        )
        await update.message.reply_text("✅ 긴급 속보가 채널에 발송되었습니다.")
    except Exception as e:
        logger.error("breaking_command error: %s", e)
        await update.message.reply_text(f"❌ 발송 실패: {e}")
