from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "🤖 <b>AI·반도체 뉴스 브리핑 봇</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "📋 <b>명령어 목록</b>\n\n"
    "/ai — AI 업계 최신 뉴스 브리핑\n"
    "/semi — 반도체 업계 최신 뉴스 브리핑\n"
    "/market — 주요 시장·증시 동향 리포트\n"
    "/notification — 정기 알림 설정\n"
    "/help — 이 도움말 보기\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "💡 <b>사용 예시</b>\n"
    "• /ai 입력 → AI 뉴스 요약 리포트 즉시 수신\n"
    "• /notification 입력 → 매일 정해진 시간에 자동 수신 설정"
)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")
