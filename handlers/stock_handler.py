import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from services.naver_stock_service import get_price, get_financial, get_market_overview, search_ticker
from services.portfolio_store import get_portfolio, add_position, remove_position
from services.gemini_service import analyze_stock, summarize_market
from utils.formatter import stock_report, stock_analyze_report, portfolio_report, market_status_report
from config import KIS_WATCHLIST

logger = logging.getLogger(__name__)

# ConversationHandler 상태
TICKER, QTY, PRICE = range(3)
STOCK_TICKER, ANALYZE_TICKER = range(3, 5)


# ── 공통 유틸 ──────────────────────────────────────────────────────────────

async def _resolve_ticker(query: str) -> str | None:
    query = query.strip()
    if query.isdigit() and len(query) == 6:
        return query
    results = await search_ticker(query)
    return results[0]["ticker"] if results else None


def _portfolio_keyboard(positions: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for pos in positions:
        rows.append([
            InlineKeyboardButton(
                f"🗑 {pos['name']} 삭제",
                callback_data=f"pf_del_{pos['ticker']}",
            )
        ])
    rows.append([InlineKeyboardButton("➕ 종목 추가", callback_data="pf_add")])
    return InlineKeyboardMarkup(rows)


async def _render_portfolio(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """포트폴리오 텍스트 + 키보드 생성"""
    positions = get_portfolio(chat_id)
    prices: dict[str, dict] = {}
    if positions:
        results = await asyncio.gather(
            *[get_price(p["ticker"]) for p in positions],
            return_exceptions=True,
        )
        for pos, result in zip(positions, results):
            if isinstance(result, dict):
                prices[pos["ticker"]] = result
    return portfolio_report(positions, prices), _portfolio_keyboard(positions)


# ── /stock ────────────────────────────────────────────────────────────────

async def _run_stock(update: Update, query: str) -> None:
    msg = await update.message.reply_text(f"🔄 <b>{query}</b> 시세 조회 중…", parse_mode="HTML")
    try:
        ticker = await _resolve_ticker(query)
        if not ticker:
            await msg.edit_text(f"⚠️ '{query}' 종목을 찾을 수 없습니다.")
            return
        data = await get_price(ticker)
        await msg.edit_text(stock_report(data), parse_mode="HTML")
    except Exception as e:
        logger.error("stock error: %s", e)
        await msg.edit_text("⚠️ 시세 조회 중 오류가 발생했습니다.")


async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.args:
        await _run_stock(update, " ".join(context.args))
        return ConversationHandler.END
    await update.message.reply_text(
        "📈 <b>시세 조회</b>\n\n"
        "종목 코드 또는 종목명을 입력하세요.\n"
        "<i>예: 005930 또는 삼성전자</i>\n\n"
        "/cancel 로 취소",
        parse_mode="HTML",
    )
    return STOCK_TICKER


async def stock_got_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await _run_stock(update, update.message.text.strip())
    return ConversationHandler.END


# ── /analyze ──────────────────────────────────────────────────────────────

async def _run_analyze(update: Update, query: str) -> None:
    msg = await update.message.reply_text(f"🔄 <b>{query}</b> AI 분석 중…", parse_mode="HTML")
    try:
        ticker = await _resolve_ticker(query)
        if not ticker:
            await msg.edit_text(f"⚠️ '{query}' 종목을 찾을 수 없습니다.")
            return
        price_data, financial_data = await asyncio.gather(
            get_price(ticker), get_financial(ticker),
        )
        sections = await analyze_stock(price_data, financial_data)
        await msg.edit_text(stock_analyze_report(price_data, sections), parse_mode="HTML")
    except Exception as e:
        logger.error("analyze error: %s", e)
        await msg.edit_text("⚠️ AI 분석 중 오류가 발생했습니다.")


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.args:
        await _run_analyze(update, " ".join(context.args))
        return ConversationHandler.END
    await update.message.reply_text(
        "🔍 <b>AI 종목 분석</b>\n\n"
        "종목 코드 또는 종목명을 입력하세요.\n"
        "<i>예: 000660 또는 SK하이닉스</i>\n\n"
        "/cancel 로 취소",
        parse_mode="HTML",
    )
    return ANALYZE_TICKER


async def analyze_got_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await _run_analyze(update, update.message.text.strip())
    return ConversationHandler.END


# ── /portfolio (조회 + 버튼) ──────────────────────────────────────────────

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("🔄 포트폴리오 조회 중…")
    try:
        text, markup = await _render_portfolio(update.effective_chat.id)
        await msg.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error("portfolio_command error: %s", e)
        await msg.edit_text("⚠️ 포트폴리오 조회 중 오류가 발생했습니다.")


# ── 삭제 버튼 콜백 ────────────────────────────────────────────────────────

async def portfolio_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    ticker = query.data.removeprefix("pf_del_")
    chat_id = query.message.chat_id

    removed = remove_position(chat_id, ticker)
    if not removed:
        await query.answer("이미 삭제된 종목입니다.", show_alert=True)
        return

    try:
        text, markup = await _render_portfolio(chat_id)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error("portfolio_delete_callback error: %s", e)


# ── 종목 추가 ConversationHandler ─────────────────────────────────────────

async def portfolio_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """'➕ 종목 추가' 버튼 → 대화 시작"""
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "➕ <b>종목 추가</b>\n\n"
        "종목 코드 6자리를 입력하세요.\n"
        "<i>예: 005930 (삼성전자), 000660 (SK하이닉스)</i>\n\n"
        "/cancel 로 취소",
        parse_mode="HTML",
    )
    return TICKER


async def portfolio_got_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    msg = await update.message.reply_text("🔄 종목 확인 중…")
    try:
        ticker = await _resolve_ticker(text)
        if not ticker:
            await msg.edit_text(f"⚠️ '{text}' 종목을 찾을 수 없습니다. 다시 입력해주세요.")
            return TICKER
        price_data = await get_price(ticker)
        name = price_data.get("name", ticker)
        context.user_data["pf_ticker"] = ticker
        context.user_data["pf_name"] = name
        await msg.edit_text(
            f"✅ <b>{name}</b> ({ticker})  현재가 {price_data.get('price')}원\n\n"
            "수량을 입력하세요. <i>예: 10</i>",
            parse_mode="HTML",
        )
        return QTY
    except Exception as e:
        logger.error("portfolio_got_ticker error: %s", e)
        await msg.edit_text("⚠️ 종목 조회 중 오류가 발생했습니다. 다시 입력해주세요.")
        return TICKER


async def portfolio_got_qty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(",", "")
    try:
        qty = int(text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ 숫자로 입력해주세요. <i>예: 10</i>", parse_mode="HTML")
        return QTY

    context.user_data["pf_qty"] = qty
    await update.message.reply_text(
        f"수량 {qty}주 확인.\n\n"
        "평균 단가를 입력하세요 (원). <i>예: 330000</i>",
        parse_mode="HTML",
    )
    return PRICE


async def portfolio_got_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(",", "").replace("원", "")
    try:
        avg_price = int(text)
        if avg_price <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ 숫자로 입력해주세요. <i>예: 330000</i>", parse_mode="HTML")
        return PRICE

    ticker = context.user_data.get("pf_ticker")
    name = context.user_data.get("pf_name", ticker)
    qty = context.user_data.get("pf_qty")
    chat_id = update.effective_chat.id

    action = add_position(chat_id, ticker, name, qty, avg_price)
    verb = "추가" if action == "added" else "평단 업데이트"
    await update.message.reply_text(
        f"✅ <b>{name}</b> {qty}주 @ {avg_price:,}원 {verb}됐습니다.",
        parse_mode="HTML",
    )

    # 업데이트된 포트폴리오 바로 표시
    try:
        text, markup = await _render_portfolio(chat_id)
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        pass

    context.user_data.clear()
    return ConversationHandler.END


async def portfolio_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ 종목 추가를 취소했습니다.")
    return ConversationHandler.END


# ── ConversationHandler 객체 (main.py에서 등록) ───────────────────────────

stock_conversation = ConversationHandler(
    entry_points=[CommandHandler("stock", stock_command)],
    states={
        STOCK_TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, stock_got_ticker)],
    },
    fallbacks=[CommandHandler("cancel", portfolio_cancel)],
    per_message=False,
)

analyze_conversation = ConversationHandler(
    entry_points=[CommandHandler("analyze", analyze_command)],
    states={
        ANALYZE_TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_got_ticker)],
    },
    fallbacks=[CommandHandler("cancel", portfolio_cancel)],
    per_message=False,
)

portfolio_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(portfolio_add_start, pattern=r"^pf_add$")],
    states={
        TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, portfolio_got_ticker)],
        QTY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, portfolio_got_qty)],
        PRICE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, portfolio_got_price)],
    },
    fallbacks=[CommandHandler("cancel", portfolio_cancel)],
    per_message=False,
)


# ── /market_status ────────────────────────────────────────────────────────

async def market_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("🔄 시황 데이터 수집 중…")
    try:
        overview = await get_market_overview(KIS_WATCHLIST)
        sections = await summarize_market(overview)
        await msg.edit_text(market_status_report(overview, sections), parse_mode="HTML")
    except Exception as e:
        logger.error("market_status_command error: %s", e)
        await msg.edit_text("⚠️ 시황 조회 중 오류가 발생했습니다.")
