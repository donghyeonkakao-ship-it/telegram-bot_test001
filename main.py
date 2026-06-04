import logging
import os
import threading

from flask import Flask
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from config import TELEGRAM_BOT_TOKEN
from handlers.ai_handler import ai_command
from handlers.breaking_news_handler import auto_breaking_job
from services.breaking_detector import warmup
from handlers.market_handler import market_command
from handlers.notification_handler import notification_callback, notification_command
from handlers.help_handler import help_command
from handlers.semi_handler import semi_command
from handlers.stock_handler import (
    analyze_conversation,
    market_status_command,
    portfolio_command,
    portfolio_conversation,
    portfolio_delete_callback,
    stock_conversation,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)


# ── Flask 웹 서버 (Render Web Service 슬립 방지) ─────────────────────────
# Render는 HTTP 포트가 열려 있어야 Web Service로 인식합니다.
# UptimeRobot이 10분마다 ping하여 15분 슬립을 방지합니다.

flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return "Bot is running", 200


@flask_app.route("/health")
def health():
    return "OK", 200


def _run_flask() -> None:
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


# ─────────────────────────────────────────────────────────────────────────


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 .env에 설정되지 않았습니다.")

    # Flask를 데몬 스레드로 실행 → 텔레그램 봇 async 루프와 충돌 없음
    threading.Thread(target=_run_flask, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 도움말
    app.add_handler(CommandHandler("help", help_command))

    # 수동 조회 명령어
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("semi", semi_command))
    app.add_handler(CommandHandler("market", market_command))

    # 주식 투자 보조
    app.add_handler(stock_conversation)
    app.add_handler(analyze_conversation)
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("market_status", market_status_command))
    app.add_handler(portfolio_conversation)
    app.add_handler(CallbackQueryHandler(portfolio_delete_callback, pattern=r"^pf_del_"))

    # 정기 알림 설정
    app.add_handler(CommandHandler("notification", notification_command))
    app.add_handler(CallbackQueryHandler(notification_callback, pattern=r"^notif_"))

    # 자동 속보 감지 (10분마다 RSS 폴링, 워밍업 후 신규 기사만 발송)
    async def _warmup_job(ctx):
        await warmup()

    app.job_queue.run_once(_warmup_job, when=0, name="breaking_warmup")
    app.job_queue.run_repeating(auto_breaking_job, interval=600, first=30, name="breaking_news")

    print("🚀 봇 시작! 명령어: /help /ai /semi /market /notification /stock /analyze /portfolio /market_status")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
