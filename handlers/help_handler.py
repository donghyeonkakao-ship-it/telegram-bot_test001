from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "🤖 <b>AI·반도체·주식 브리핑 봇</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"

    "📰 <b>뉴스 브리핑</b>\n"
    "/ai — AI 업계 최신 뉴스 브리핑\n"
    "/semi — 반도체 업계 최신 뉴스 브리핑\n"
    "/market — AI·반도체 시장 분석 가이드\n"
    "/notification — 정기 뉴스 다이제스트 알림 설정\n\n"

    "📈 <b>주식 투자 보조</b>\n"
    "/stock <code>[종목코드]</code> — 시세 조회\n"
    "└ 예: <code>/stock 005930</code>\n"
    "/analyze <code>[종목코드]</code> — AI 종목 분석\n"
    "└ 예: <code>/analyze 000660</code>\n"
    "/portfolio — 보유 종목 수익률 현황\n"
    "└ 버튼으로 추가·삭제 가능\n"
    "/market_status — 코스피·코스닥 시황 브리핑\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    "💡 <b>주요 종목 코드</b>\n"
    "• 삼성전자 <code>005930</code>\n"
    "• SK하이닉스 <code>000660</code>\n"
    "• NAVER <code>035420</code>\n"
    "• 현대차 <code>005380</code>\n"
    "• LG화학 <code>051910</code>"
)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML", disable_web_page_preview=True)
