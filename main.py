import os
import logging
import asyncio
import feedparser
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. 설정 및 환경변수 로드
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
SENT_LOG_FILE = "sent_urls.txt"

# 로그 설정 (에러 확인용)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 중복 발송 방지용 함수들
def get_sent_urls():
    if not os.path.exists(SENT_LOG_FILE):
        return set()

    with open(SENT_LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


def save_sent_url(url: str):
    with open(SENT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


# [공통 뉴스 수집 함수] 구글 뉴스에서 데이터 긁어오기
def fetch_latest_news():
    rss_url = "https://news.google.com/rss/search?q=AI+반도체&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    return feed.entries[:5]  # 최신 뉴스 5개 반환


# 2. 새로운 기능: /news 명령어를 치면 실행되는 함수
async def manual_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 최신 AI 반도체 뉴스를 가져오는 중입니다. 잠시만 기다려주세요..."
    )

    entries = fetch_latest_news()
    for entry in entries:
        message = (
            f"📰 **[요청하신 최신 뉴스]**\n\n"
            f"📌 {entry.title}\n\n"
            f"🔗 [기사 원문 보기]({entry.link})"
        )
        await update.message.reply_text(text=message, parse_mode="Markdown")
        await asyncio.sleep(0.5)


# 3. 기존 기능: 10분마다 자동으로 채널에 뉴스 쏘는 함수
async def check_and_send_news(context: ContextTypes.DEFAULT_TYPE):
    logging.info("📰 [자동 스케줄러] 구글 뉴스 수집 중...")
    entries = fetch_latest_news()
    sent_urls = get_sent_urls()
    count = 0

    for entry in entries:
        if entry.link in sent_urls:
            continue

        message = (
            f"📰 **[실시간 AI 반도체 뉴스]**\n\n"
            f"📌 {entry.title}\n\n"
            f"🔗 [기사 원문 보기]({entry.link})"
        )

        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
            save_sent_url(entry.link)
            count += 1
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"❌ 발송 실패: {e}")

    if count == 0:
        logging.info("🆕 새로 추가된 자동 뉴스가 없습니다.")


# 4. 메인 실행 함수
def main():
    if not TOKEN or not CHANNEL_ID:
        print("❌ 에러: .env 파일에 토큰이나 채널 ID가 올바르게 입력되지 않았습니다.")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("news", manual_news_command))

    job_queue = app.job_queue
    job_queue.run_repeating(check_and_send_news, interval=600, first=3)

    print("🚀 봇이 다시 켜졌습니다! 채널 자동 전송 및 /news 명령어 대기 중...")
    app.run_polling()


if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                                                                                                                        