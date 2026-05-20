import asyncio
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)

_AI_SYSTEM_PROMPT = """당신은 AI 산업 전문 애널리스트입니다.
제공된 뉴스 헤드라인을 분석해 한국어 브리핑 리포트를 작성하세요.
반드시 아래 구조를 따르세요 (텔레그램 HTML 태그 사용 금지, 순수 텍스트만):

[오늘의 핵심 동향]
핵심 내용 2~3문장

[AGI 진행 상황]
현재 AI 발전 단계 및 AGI를 향한 주요 이정표 분석

[주요 기업 동향]
• 기업명: 동향 요약
• (3~5개 항목)

[시장 영향]
투자자·산업 관점에서 시사점 1~2문장

간결하고 날카롭게, 전문 투자자 눈높이로 작성하세요."""

_SEMI_SYSTEM_PROMPT = """당신은 반도체 산업 전문 애널리스트입니다.
제공된 뉴스 헤드라인을 분석해 한국어 브리핑 리포트를 작성하세요.
반드시 아래 구조를 따르세요 (텔레그램 HTML 태그 사용 금지, 순수 텍스트만):

[오늘의 핵심 동향]
반도체 시장 핵심 내용 2~3문장

[수급 및 공급망]
TSMC·CoWoS·HBM·리드타임 등 현황

[주요 기업 동향]
• 기업명: 동향 요약
• (TSMC, 삼성, SK하이닉스, 엔비디아, ASML 등 해당 기업 위주)

[업황 전망]
단기 수급·가격·투자 관점 1~2문장

간결하고 날카롭게, 전문 투자자 눈높이로 작성하세요."""

_DIGEST_SYSTEM_PROMPT = """당신은 AI·반도체 시장 전문 애널리스트입니다.
제공된 뉴스 헤드라인을 분석해 AI파트와 반도체파트로 나눠 한국어 다이제스트를 작성하세요.
순수 텍스트만 사용 (HTML 태그 금지). 각 파트 3~5문장으로 간결하게 작성하세요."""


def _build_article_text(articles: list[dict]) -> str:
    return "\n".join(f"- {a['title']} [{a['source']}]" for a in articles if a.get("title"))


def _generate_sync(prompt: str) -> str:
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text


async def _generate(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate_sync, prompt)


async def summarize_ai_news(articles: list[dict]) -> str:
    article_text = _build_article_text(articles)
    prompt = f"{_AI_SYSTEM_PROMPT}\n\n뉴스 목록:\n{article_text}"
    return await _generate(prompt)


async def summarize_semi_news(articles: list[dict]) -> str:
    article_text = _build_article_text(articles)
    prompt = f"{_SEMI_SYSTEM_PROMPT}\n\n뉴스 목록:\n{article_text}"
    return await _generate(prompt)


async def summarize_digest(ai_articles: list[dict], semi_articles: list[dict]) -> tuple[str, str]:
    ai_text = _build_article_text(ai_articles)
    semi_text = _build_article_text(semi_articles)
    prompt = (
        f"{_DIGEST_SYSTEM_PROMPT}\n\n"
        f"[AI 뉴스]\n{ai_text}\n\n"
        f"[반도체 뉴스]\n{semi_text}\n\n"
        f"'AI파트:' 와 '반도체파트:' 레이블로 구분해서 작성하세요."
    )
    raw = await _generate(prompt)

    ai_part, semi_part = raw, raw
    if "반도체파트:" in raw:
        parts = raw.split("반도체파트:", 1)
        ai_part = parts[0].replace("AI파트:", "").strip()
        semi_part = parts[1].strip()
    elif "AI파트:" in raw:
        ai_part = raw.split("AI파트:", 1)[1].strip()

    return ai_part, semi_part
