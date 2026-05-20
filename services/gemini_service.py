import asyncio
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)

# 섹션 구분자 기반 출력 → formatter가 파싱 후 HTML 적용
_AI_SYSTEM_PROMPT = """당신은 AI 산업 전문 애널리스트입니다.
아래 뉴스 헤드라인을 분석해 한국어 브리핑을 작성하세요.

규칙:
- 마크다운(**, *, #) 절대 사용 금지
- 이모지 사용 금지
- 각 섹션은 반드시 아래 구분자로 시작
- 기업 동향은 "기업명: 한 줄" 형식, 최대 4개
- 전체 길이 300자 이내로 간결하게

출력 형식:
##TREND##
핵심 동향 2문장

##AGI##
AGI 진행 상황 1~2문장

##COMPANIES##
기업명: 내용
기업명: 내용

##IMPACT##
시장 시사점 1문장"""

_SEMI_SYSTEM_PROMPT = """당신은 반도체 산업 전문 애널리스트입니다.
아래 뉴스 헤드라인을 분석해 한국어 브리핑을 작성하세요.

규칙:
- 마크다운(**, *, #) 절대 사용 금지
- 이모지 사용 금지
- 각 섹션은 반드시 아래 구분자로 시작
- 기업 동향은 "기업명: 한 줄" 형식, 최대 4개
- 전체 길이 300자 이내로 간결하게

출력 형식:
##TREND##
핵심 동향 2문장

##SUPPLY##
수급·공급망 현황 1~2문장

##COMPANIES##
기업명: 내용
기업명: 내용

##OUTLOOK##
업황 전망 1문장"""

_DIGEST_SYSTEM_PROMPT = """당신은 AI·반도체 시장 전문 애널리스트입니다.
마크다운(**, *, #) 절대 사용 금지. 이모지 사용 금지.

AI파트와 반도체파트 각각 3문장 이내로 간결하게 작성하세요.

출력 형식:
##AI##
AI 동향 요약

##SEMI##
반도체 동향 요약"""


def _build_article_text(articles: list[dict]) -> str:
    return "\n".join(f"- {a['title']} [{a['source']}]" for a in articles if a.get("title"))


def _parse_sections(raw: str) -> dict[str, str]:
    """##SECTION## 구분자로 텍스트를 섹션별로 파싱합니다."""
    sections: dict[str, str] = {}
    current_key = None
    buffer: list[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("##") and line.endswith("##"):
            if current_key:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = line.strip("#")
            buffer = []
        elif current_key:
            buffer.append(line)

    if current_key:
        sections[current_key] = "\n".join(buffer).strip()

    return sections


def _generate_sync(prompt: str) -> str:
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text


async def _generate(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate_sync, prompt)


async def summarize_ai_news(articles: list[dict]) -> dict[str, str]:
    article_text = _build_article_text(articles)
    prompt = f"{_AI_SYSTEM_PROMPT}\n\n뉴스 목록:\n{article_text}"
    raw = await _generate(prompt)
    return _parse_sections(raw)


async def summarize_semi_news(articles: list[dict]) -> dict[str, str]:
    article_text = _build_article_text(articles)
    prompt = f"{_SEMI_SYSTEM_PROMPT}\n\n뉴스 목록:\n{article_text}"
    raw = await _generate(prompt)
    return _parse_sections(raw)


async def summarize_digest(ai_articles: list[dict], semi_articles: list[dict]) -> tuple[str, str]:
    ai_text = _build_article_text(ai_articles)
    semi_text = _build_article_text(semi_articles)
    prompt = (
        f"{_DIGEST_SYSTEM_PROMPT}\n\n"
        f"[AI 뉴스]\n{ai_text}\n\n"
        f"[반도체 뉴스]\n{semi_text}"
    )
    raw = await _generate(prompt)
    sections = _parse_sections(raw)
    return sections.get("AI", raw), sections.get("SEMI", "")
