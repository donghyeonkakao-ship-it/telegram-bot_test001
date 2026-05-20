from telegram import Update
from telegram.ext import ContextTypes

# /market 명령어의 정적 분석 콘텐츠 (HTML 포맷)
MARKET_REPORT = """📊 <b>AI 반도체 시장 종합 분석 가이드</b>
━━━━━━━━━━━━━━━━━━

<blockquote>AI 반도체 시장을 정확히 읽으려면 거시적 환경(질적 요인)과 핵심 정량 지표(양적 데이터)를 4대 핵심 축으로 다각도 분석해야 합니다.</blockquote>

━━━━━━━━━━━━━━━━━━
📌 <b>1. 자본 흐름 및 전방 산업 투자</b>
<i>Capital &amp; Demand Source</i>

<blockquote>핵심 질문: "AI 시장의 큰손들은 어디에, 얼마나 지출하고 있으며 그 투자는 지속 가능한가?"</blockquote>

🔎 <b>분석 포인트</b>
• <b>빅테크 인프라 확장:</b> MS·구글·메타·아마존의 데이터센터 건설 및 서버 확충 속도
• <b>AI 서비스 ROI:</b> 막대한 투자 대비 생성형 AI 비즈니스 수익성 추적 → 정체 시 수요 급랭 리스크
• <b>대안 자본 흐름:</b> AI 반도체 설계 스타트업 VC 자금 유입 및 IPO 동향

📈 <b>핵심 지표</b>
• 하이퍼스케일러 CAPEX → <b>연간 6,000억 달러 돌파 추이</b> 모니터링

━━━━━━━━━━━━━━━━━━
📌 <b>2. 수급량 및 공급망 가치사슬</b>
<i>Supply &amp; Bottleneck</i>

<blockquote>핵심 질문: "수요를 감당할 만큼 제품이 잘 만들어지고 있는가? 어디서 병목이 생기는가?"</blockquote>

🔎 <b>분석 포인트</b>
• <b>독점 파운드리·첨단 패키징:</b> TSMC 미세 공정 능력 및 CoWoS 생산 한계
• <b>HBM 생태계:</b> HBM 세대교체(HBM3E → HBM4) 트렌드 및 메모리 3사 퀄 테스트 현황

📈 <b>핵심 지표</b>
• TSMC CoWoS 가동률 및 캐파
• HBM 가격 프리미엄 → <b>범용 대비 3~5배 수준</b>
• 제조 리드 타임(Lead Time) 변화

━━━━━━━━━━━━━━━━━━
📌 <b>3. 기술 트렌드 및 구조적 전환</b>
<i>Technology Shift</i>

<blockquote>핵심 질문: "반도체 수요의 질적 변화는 어디로 향하고 있는가?"</blockquote>

🔎 <b>분석 포인트</b>
• <b>학습 → 추론 중심 전환:</b> 고가 GPU에서 전력 효율 NPU 비중 확대
• <b>빅테크 자체 칩 독립:</b> 구글(TPU)·아마존(Trainium)·메타(MTIA) 도입 비중 추적
• <b>온디바이스 AI 확산:</b> 스마트폰·PC·자동차용 저전력 AI 반도체 시장 성장

📈 <b>핵심 지표</b>
• AI 칩 시장 매출 비중 → <b>전체 반도체 시장의 약 50%, 5,000억 달러 돌파 흐름</b> 추적

━━━━━━━━━━━━━━━━━━
📌 <b>4. 지정학적 리스크 및 제도적 변수</b>
<i>Macro &amp; Geopolitics</i>

<blockquote>핵심 질문: "기술 외적인 정치·환경적 요인이 공급망을 어떻게 흔들고 있는가?"</blockquote>

🔎 <b>분석 포인트</b>
• <b>미·중 기술 패권 전쟁:</b> 대중국 반도체·장비 수출 규제 수위 및 중국 자급률 변화
• <b>주요국 보조금 정책:</b> 미국 Chips Act·EU·일본·한국 보조금이 팹 증설 위치에 미치는 영향
• <b>인프라 한계:</b> AI 데이터센터 전력 소모 폭증 → 국가별 전력망 규제 및 변압기 공급 부족

📈 <b>핵심 지표</b>
• 필라델피아 반도체 지수(SOX) 동향
• 글로벌 반도체 장비 매출액(SEMI Billings)

━━━━━━━━━━━━━━━━━━
<i>🔄 본 가이드는 정기적으로 업데이트됩니다. 실시간 데이터는 /ai 및 /semi 명령어를 활용하세요.</i>"""


async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        MARKET_REPORT,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
