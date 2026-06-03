import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from services.naver_stock_service import get_price, get_financial, get_market_overview, search_ticker
from services.portfolio_store import get_portfolio, add_position, remove_position
from services.gemini_service import analyze_stock, summarize_market
from utils.formatter import stock_report, stock_analyze_report, portfolio_report, market_status_report
from config import KIS_WATCHLIST

logger = logging.getLogger(__name__)


async def _resolve_ticker(query: str) -> str | None:
    """숫자 6자리면 그대로, 아니면 이름 검색"""
    query = query.strip()
    if query.isdigit() and len(query) == 6:
        return query
    results = await search_ticker(query)
    return results[0]["ticker"] if results else None


# ── /stock ────────────────────────────────────────────────────────────────

async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "사용법: <code>/stock 005930</code> 또는 <code>/stock 삼성전자</code>",
            parse_mode="HTML",
        )
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔄 <b>{query}</b> 시세 조회 중…", parse_mode="HTML")

    try:
        ticker = await _resolve_ticker(query)
        if not ticker:
            await msg.edit_text(f"⚠️ '{query}' 종목을 찾을 수 없습니다.")
            return

        data = await get_price(ticker)
        await msg.edit_text(stock_report(data), parse_mode="HTML")

    except Exception as e:
        logger.error("stock_command error: %s", e)
        await msg.edit_text("⚠️ 시세 조회 중 오류가 발생했습니다.")


# ── /analyze ──────────────────────────────────────────────────────────────

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "사용법: <code>/analyze 005930</code> 또는 <code>/analyze 삼성전자</code>",
            parse_mode="HTML",
        )
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔄 <b>{query}</b> AI 분석 중…", parse_mode="HTML")

    try:
        ticker = await _resolve_ticker(query)
        if not ticker:
            await msg.edit_text(f"⚠️ '{query}' 종목을 찾을 수 없습니다.")
            return

        price_data, financial_data = await asyncio.gather(
            get_price(ticker),
            get_financial(ticker),
        )
        sections = await analyze_stock(price_data, financial_data)
        await msg.edit_text(
            stock_analyze_report(price_data, sections),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error("analyze_command error: %s", e)
        await msg.edit_text("⚠️ AI 분석 중 오류가 발생했습니다.")


# ── /portfolio ────────────────────────────────────────────────────────────

_PORTFOLIO_HELP = (
    "📂 <b>포트폴리오 명령어</b>\n\n"
    "<code>/portfolio</code> — 현황 보기\n"
    "<code>/portfolio add 005930 10 85000</code> — 종목 추가 (종목코드 수량 평균단가)\n"
    "<code>/portfolio remove 005930</code> — 종목 제거"
)


async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args or []

    # 서브커맨드 없으면 현황 조회
    if not args or args[0] == "show":
        await _portfolio_show(update, chat_id)
        return

    if args[0] == "add":
        await _portfolio_add(update, chat_id, args[1:])
        return

    if args[0] == "remove":
        await _portfolio_remove(update, chat_id, args[1:])
        return

    await update.message.reply_text(_PORTFOLIO_HELP, parse_mode="HTML")


async def _portfolio_show(update: Update, chat_id: int) -> None:
    positions = get_portfolio(chat_id)
    msg = await update.message.reply_text("🔄 포트폴리오 시세 조회 중…")

    prices: dict[str, dict] = {}
    if positions:
        tasks = [get_price(p["ticker"]) for p in positions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for pos, result in zip(positions, results):
            if isinstance(result, dict):
                prices[pos["ticker"]] = result

    await msg.edit_text(
        portfolio_report(positions, prices),
        parse_mode="HTML",
    )


async def _portfolio_add(update: Update, chat_id: int, args: list[str]) -> None:
    if len(args) < 3:
        await update.message.reply_text(
            "사용법: <code>/portfolio add 005930 10 85000</code>",
            parse_mode="HTML",
        )
        return

    ticker_query, qty_str, price_str = args[0], args[1], args[2]
    try:
        qty = int(qty_str)
        avg_price = int(price_str.replace(",", ""))
    except ValueError:
        await update.message.reply_text("⚠️ 수량과 평균단가는 숫자로 입력해주세요.")
        return

    msg = await update.message.reply_text("🔄 종목 확인 중…")
    try:
        ticker = await _resolve_ticker(ticker_query)
        if not ticker:
            await msg.edit_text(f"⚠️ '{ticker_query}' 종목을 찾을 수 없습니다.")
            return

        price_data = await get_price(ticker)
        name = price_data.get("name", ticker)
        action = add_position(chat_id, ticker, name, qty, avg_price)

        verb = "추가" if action == "added" else "업데이트"
        await msg.edit_text(
            f"✅ <b>{name}</b> ({ticker}) {qty}주 @ {avg_price:,}원 {verb}됐습니다.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("portfolio_add error: %s", e)
        await msg.edit_text("⚠️ 종목 추가 중 오류가 발생했습니다.")


async def _portfolio_remove(update: Update, chat_id: int, args: list[str]) -> None:
    if not args:
        await update.message.reply_text(
            "사용법: <code>/portfolio remove 005930</code>",
            parse_mode="HTML",
        )
        return

    ticker = args[0].strip()
    removed = remove_position(chat_id, ticker)
    if removed:
        await update.message.reply_text(f"🗑 <b>{ticker}</b> 포트폴리오에서 제거했습니다.", parse_mode="HTML")
    else:
        await update.message.reply_text(f"⚠️ <b>{ticker}</b>는 포트폴리오에 없습니다.", parse_mode="HTML")


# ── /market_status ────────────────────────────────────────────────────────

async def market_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("🔄 시황 데이터 수집 중…")
    try:
        overview = await get_market_overview(KIS_WATCHLIST)
        sections = await summarize_market(overview)
        await msg.edit_text(
            market_status_report(overview, sections),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("market_status_command error: %s", e)
        await msg.edit_text("⚠️ 시황 조회 중 오류가 발생했습니다.")
