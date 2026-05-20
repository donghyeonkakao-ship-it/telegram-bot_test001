import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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


# ── Render Web Service 유지용 헬스체크 서버 ──────────────────────────────
# Render는 Web Service 타입을 유지하려면 HTTP 포트가 열려 있어야 합니다.
# UptimeRobot이 10분마다 이 엔드포인트를 ping해 슬립을 방지합니다.

class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

    def log_message(self, *args):
        pass  # HTTP 요청 로그 노이즈 억제


def _start_health_server() -> None:
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    logging.getLogger(__name__).info("헬스체크 서버 시작: port=%d", port)
    server.serve_forever()


# ─────────────────────────────────────────────────────────────────────────


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 .env에 설정되지 않았습니다.")

    # 헬스체크 서버를 데몬 스레드로 실행 (봇 종료 시 자동 소멸)
    threading.Thread(target=_start_health_server, daemon=True).start()

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
