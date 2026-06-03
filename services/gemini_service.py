import asyncio
import time
import logging
from google import genai
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

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

규칙:
- 반드시 구체적인 기업명, 제품명, 기술명, 이벤트명을 명시
- 추상적 표현("주요 기업들", "일부 기업" 등) 사용 금지
- 기업 동향은 "기업명: 구체적 행동/발표" 형식, 각 파트 최대 3개
- 각 섹션은 반드시 아래 구분자로 시작

출력 형식:
##AI_TREND##
AI 핵심 동향 2문장 (구체적 기업명·제품명·기술명 포함)

##AI_COMPANIES##
기업명: 구체적 행동 또는 발표 내용
기업명: 구체적 행동 또는 발표 내용
기업명: 구체적 행동 또는 발표 내용

##SEMI_TREND##
반도체 핵심 동향 2문장 (구체적 기업명·제품명·이벤트명 포함)

##SEMI_COMPANIES##
기업명: 구체적 행동 또는 발표 내용
기업명: 구체적 행동 또는 발표 내용
기업명: 구체적 행동 또는 발표 내용

##SEMI_TECH##
주목 기술 또는 이슈 1문장 (구체적 기술명 포함)"""


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
    delays = [5, 15, 30]
    for attempt, delay in enumerate(delays, start=1):
        try:
            response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text
        except (ServiceUnavailable, ResourceExhausted) as e:
            if attempt == len(delays):
                raise
            logger.warning("Gemini 503/429 (시도 %d/%d), %ds 후 재시도: %s", attempt, len(delays), delay, e)
            time.sleep(delay)
    raise RuntimeError("Gemini 재시도 초과")


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


_STOCK_ANALYSIS_PROMPT = """당신은 한국 주식 전문 애널리스트입니다.
아래 종목의 시세 및 재무지표를 분석해 한국어 투자 의견을 작성하세요.

규칙:
- 마크다운(**, *, #) 절대 사용 금지, 이모지 사용 금지
- 구체적인 수치 근거를 반드시 포함
- 투자 의견은 긍정/중립/부정 중 하나로 명확히 제시
- 각 섹션은 반드시 아래 구분자로 시작

출력 형식:
##VALUATION##
밸류에이션 평가 2문장 (PER·PBR 수치 기반, 동종업계 비교)

##STRENGTH##
투자 포인트 2문장 (구체적 지표·사업 근거)

##RISK##
리스크 요인 1~2문장

##OPINION##
종합 투자 의견 1문장 (긍정/중립/부정 명시)"""


_MARKET_SUMMARY_PROMPT = """당신은 한국 주식시장 전문 애널리스트입니다.
아래 코스피/코스닥 지수 및 주요 종목 데이터를 분석해 시황 브리핑을 작성하세요.

규칙:
- 마크다운(**, *, #) 절대 사용 금지, 이모지 사용 금지
- 구체적인 수치와 종목명 반드시 포함

출력 형식:
##INDEX##
지수 현황 2문장 (코스피·코스닥 수치 기반)

##THEME##
오늘의 주요 테마·섹터 동향 2문장

##PICKS##
주목 종목 3개, 형식: 종목명(등락률): 한 줄 코멘트

##OUTLOOK##
단기 시장 전망 1문장"""


_BREAKING_PROMPT = """아래 기사 제목을 한국어로 분석하세요.
규칙: 마크다운(**, *, #) 절대 사용 금지, 이모지 사용 금지

출력 형식:
##SUMMARY##
무슨 일이 있었는지 1문장

##IMPACT##
왜 중요한지 시장·업계 관점 1문장"""


async def summarize_breaking_article(title: str, source: str) -> dict[str, str]:
    prompt = f"{_BREAKING_PROMPT}\n\n기사 제목: {title}\n출처: {source}"
    raw = await _generate(prompt)
    return _parse_sections(raw)


async def analyze_stock(price_data: dict, financial_data: dict) -> dict[str, str]:
    lines = [
        f"종목명: {price_data.get('name')} ({price_data.get('ticker')})",
        f"현재가: {price_data.get('price')}원  전일대비: {price_data.get('sign')}{price_data.get('change_rate')}%",
        f"PER: {price_data.get('per')}  PBR: {price_data.get('pbr')}",
        f"시가총액: {price_data.get('market_cap')}",
        f"52주 고가: {price_data.get('w52_high')}  52주 저가: {price_data.get('w52_low')}",
    ]
    if financial_data:
        lines += [
            f"ROE: {financial_data.get('roe')}%",
            f"부채비율: {financial_data.get('debt_ratio')}%",
            f"영업이익률: {financial_data.get('operating_margin')}%",
            f"순이익률: {financial_data.get('net_margin')}%",
            f"EPS: {financial_data.get('eps')}원",
        ]
    prompt = f"{_STOCK_ANALYSIS_PROMPT}\n\n[종목 데이터]\n" + "\n".join(lines)
    raw = await _generate(prompt)
    return _parse_sections(raw)


async def summarize_market(overview: dict) -> dict[str, str]:
    kospi = overview.get("kospi", {})
    kosdaq = overview.get("kosdaq", {})
    stocks = overview.get("stocks", {})

    lines = [
        f"코스피: {kospi.get('price')} ({kospi.get('sign')}{kospi.get('change_rate')}%)",
        f"코스닥: {kosdaq.get('price')} ({kosdaq.get('sign')}{kosdaq.get('change_rate')}%)",
        "",
        "[주요 종목]",
    ]
    for data in stocks.values():
        lines.append(
            f"{data.get('name')}({data.get('ticker')}): "
            f"{data.get('price')}원 {data.get('sign')}{data.get('change_rate')}% "
            f"PER {data.get('per')}"
        )
    prompt = f"{_MARKET_SUMMARY_PROMPT}\n\n" + "\n".join(lines)
    raw = await _generate(prompt)
    return _parse_sections(raw)


async def summarize_digest(ai_articles: list[dict], semi_articles: list[dict]) -> dict[str, str]:
    ai_text = _build_article_text(ai_articles)
    semi_text = _build_article_text(semi_articles)
    prompt = (
        f"{_DIGEST_SYSTEM_PROMPT}\n\n"
        f"[AI 뉴스]\n{ai_text}\n\n"
        f"[반도체 뉴스]\n{semi_text}"
    )
    raw = await _generate(prompt)
    return _parse_sections(raw)
