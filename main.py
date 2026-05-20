import logging
import os
import threading

from flask import Flask
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from config import TELEGRAM_BOT_TOKEN
from handlers.ai_handler import ai_command
from handlers.breaking_news_handler import breaking_command
from handlers.market_handler import market_command
from handlers.notification_handler import notification_callback, notification_command
from handlers.semi_handler import semi_command

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

    # 수동 조회 명령어
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("semi", semi_command))
    app.add_handler(CommandHandler("market", market_command))

    # 정기 알림 설정
    app.add_handler(CommandHandler("notification", notification_command))
    app.add_handler(CallbackQueryHandler(notification_callback, pattern=r"^notif_"))

    # 긴급 속보 (관리자 전용)
    app.add_handler(CommandHandler("breaking", breaking_command))

    print("🚀 봇 시작! 명령어: /ai /semi /market /notification /breaking")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
