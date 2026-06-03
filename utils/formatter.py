from html import escape


def _s(text: str) -> str:
    return escape(str(text).strip())


def _companies_html(raw: str) -> str:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    out = []
    for line in lines:
        if ":" in line:
            name, _, desc = line.partition(":")
            out.append(f"• <b>{_s(name.strip())}</b>: {_s(desc.strip())}")
        else:
            out.append(f"• {_s(line)}")
    return "\n".join(out)


def _article_links(articles: list[dict], limit: int = 5) -> str:
    lines = []
    for a in articles[:limit]:
        title = _s(a["title"][:60]) + ("…" if len(a["title"]) > 60 else "")
        link = a.get("link", "")
        source = _s(a.get("source", ""))
        if link:
            lines.append(f'• <a href="{link}">{title}</a> <i>[{source}]</i>')
        else:
            lines.append(f"• {title} <i>[{source}]</i>")
    return "\n".join(lines)


def ai_report(sections: dict[str, str], articles: list[dict]) -> str:
    trend    = _s(sections.get("TREND", "—"))
    agi      = _s(sections.get("AGI", "—"))
    companies = _companies_html(sections.get("COMPANIES", ""))
    impact   = _s(sections.get("IMPACT", "—"))
    links    = _article_links(articles)

    return (
        "🤖 <b>AI 브리핑 리포트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 <b>핵심 동향</b>\n{trend}\n\n"
        f"🧠 <b>AGI 진행 상황</b>\n{agi}\n\n"
        f"📊 <b>기업 동향</b>\n{companies}\n\n"
        f"⚡ <b>시장 시사점</b>\n{impact}\n\n"
        f"📎 <b>참고 기사</b>\n{links}"
    )


def semi_report(sections: dict[str, str], articles: list[dict]) -> str:
    trend    = _s(sections.get("TREND", "—"))
    supply   = _s(sections.get("SUPPLY", "—"))
    companies = _companies_html(sections.get("COMPANIES", ""))
    outlook  = _s(sections.get("OUTLOOK", "—"))
    links    = _article_links(articles)

    return (
        "💾 <b>반도체 브리핑 리포트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 <b>핵심 동향</b>\n{trend}\n\n"
        f"🔗 <b>수급 · 공급망</b>\n{supply}\n\n"
        f"📊 <b>기업 동향</b>\n{companies}\n\n"
        f"📈 <b>업황 전망</b>\n{outlook}\n\n"
        f"📎 <b>참고 기사</b>\n{links}"
    )


def digest_report(sections: dict[str, str]) -> str:
    ai_trend     = _s(sections.get("AI_TREND", "—"))
    ai_companies = _companies_html(sections.get("AI_COMPANIES", ""))
    semi_trend   = _s(sections.get("SEMI_TREND", "—"))
    semi_cos     = _companies_html(sections.get("SEMI_COMPANIES", ""))
    semi_tech    = _s(sections.get("SEMI_TECH", ""))

    parts = [
        "📬 <b>정기 뉴스 다이제스트</b>",
        "━━━━━━━━━━━━━━━━━━",
        "",
        f"🤖 <b>AI 동향</b>\n{ai_trend}",
    ]
    if ai_companies:
        parts.append(f"\n<b>주목 기업</b>\n{ai_companies}")
    parts += [
        "",
        "━━━━━━━━━━━━━━━━━━",
        "",
        f"💾 <b>반도체 동향</b>\n{semi_trend}",
    ]
    if semi_cos:
        parts.append(f"\n<b>주목 기업</b>\n{semi_cos}")
    if semi_tech:
        parts.append(f"\n🔬 <b>주목 기술</b>\n{semi_tech}")

    return "\n".join(parts)


def stock_report(data: dict) -> str:
    sign = data.get("sign", "")
    rate = data.get("change_rate", "0")
    change = data.get("change", "0")
    sign_label = f"{sign}{change}원 ({sign}{rate}%)" if sign else f"{change}원 ({rate}%)"

    per_fwd = data.get("per_fwd", "—")
    per_fwd_str = f"  추정PER {_s(per_fwd)}" if per_fwd != "—" else ""
    div = data.get("dividend_yield", "—")

    return (
        f"📈 <b>{_s(data.get('name'))} ({_s(data.get('ticker'))})</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>현재가</b>  {_s(data.get('price'))}원  <b>{sign_label}</b>\n\n"
        f"시가 {_s(data.get('open'))}  고가 {_s(data.get('high'))}  저가 {_s(data.get('low'))}\n"
        f"거래량: {_s(data.get('volume'))}  대금: {_s(data.get('trade_value'))}\n"
        f"시가총액: {_s(data.get('market_cap'))}  외인소진율: {_s(data.get('foreign_rate'))}\n\n"
        f"📊 <b>밸류에이션</b>\n"
        f"PER {_s(data.get('per'))}{per_fwd_str}  PBR {_s(data.get('pbr'))}\n"
        f"EPS {_s(data.get('eps'))}원  BPS {_s(data.get('bps'))}원  배당수익률 {_s(div)}\n"
        f"52주 고가 {_s(data.get('w52_high'))}  저가 {_s(data.get('w52_low'))}"
    )


def stock_analyze_report(price_data: dict, sections: dict) -> str:
    name = _s(price_data.get("name"))
    ticker = _s(price_data.get("ticker"))
    valuation = _s(sections.get("VALUATION", "—"))
    strength = _s(sections.get("STRENGTH", "—"))
    risk = _s(sections.get("RISK", "—"))
    opinion = _s(sections.get("OPINION", "—"))

    return (
        f"🔍 <b>{name} ({ticker}) AI 분석</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💹 <b>밸류에이션</b>\n{valuation}\n\n"
        f"✅ <b>투자 포인트</b>\n{strength}\n\n"
        f"⚠️ <b>리스크</b>\n{risk}\n\n"
        f"🎯 <b>종합 의견</b>\n{opinion}"
    )


def portfolio_report(positions: list[dict], prices: dict[str, dict]) -> str:
    if not positions:
        return (
            "📂 <b>포트폴리오</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "보유 종목이 없습니다.\n"
            "<i>/portfolio add 005930 10 85000 으로 추가하세요.</i>"
        )

    lines = ["📂 <b>포트폴리오</b>", "━━━━━━━━━━━━━━━━━━", ""]
    total_eval = 0
    total_cost = 0

    for pos in positions:
        ticker = pos["ticker"]
        name = pos["name"]
        qty = pos["qty"]
        avg = pos["avg_price"]
        price_data = prices.get(ticker, {})
        cur_str = price_data.get("price", "")
        try:
            cur = int(str(cur_str).replace(",", ""))
        except (ValueError, TypeError):
            cur = 0

        cost = avg * qty
        eval_val = cur * qty if cur else 0
        pl = eval_val - cost
        pl_rate = (pl / cost * 100) if cost else 0

        total_eval += eval_val
        total_cost += cost

        if cur:
            sign = "▲" if pl >= 0 else "▼"
            lines.append(
                f"• <b>{_s(name)}</b> ({ticker})\n"
                f"  {qty}주 | 평단 {avg:,}원 → 현재 {cur:,}원\n"
                f"  평가손익 {sign}{abs(pl):,}원 ({pl_rate:+.1f}%)"
            )
        else:
            lines.append(
                f"• <b>{_s(name)}</b> ({ticker})\n"
                f"  {qty}주 | 평단 {avg:,}원 | <i>시세 조회 실패</i>"
            )

    if total_cost:
        total_pl = total_eval - total_cost
        total_rate = total_pl / total_cost * 100
        sign = "▲" if total_pl >= 0 else "▼"
        lines += [
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"총 평가금액 <b>{total_eval:,}원</b>",
            f"총 손익 {sign}{abs(total_pl):,}원 ({total_rate:+.1f}%)",
        ]

    return "\n".join(lines)


def market_status_report(overview: dict, sections: dict) -> str:
    kospi = overview.get("kospi", {})
    kosdaq = overview.get("kosdaq", {})

    def idx_line(d: dict) -> str:
        sign = d.get("sign", "")
        return f"{d.get('price', '—')} {sign}{d.get('change_rate', '—')}%"

    index_txt = _s(sections.get("INDEX", "—"))
    theme_txt = _s(sections.get("THEME", "—"))
    picks_txt = sections.get("PICKS", "")
    outlook_txt = _s(sections.get("OUTLOOK", "—"))

    picks_html = _companies_html(picks_txt) if picks_txt else "—"

    return (
        "📊 <b>오늘의 시황 브리핑</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"코스피 {idx_line(kospi)}  |  코스닥 {idx_line(kosdaq)}\n\n"
        f"📰 <b>지수 현황</b>\n{index_txt}\n\n"
        f"🎨 <b>테마·섹터</b>\n{theme_txt}\n\n"
        f"⭐ <b>주목 종목</b>\n{picks_html}\n\n"
        f"🔭 <b>단기 전망</b>\n{outlook_txt}"
    )


def breaking_news_auto(title: str, summary: str, impact: str, source: str, link: str) -> str:
    title_html = _s(title)
    linked = f'<a href="{link}">{title_html}</a>' if link else title_html
    return (
        f"🚨 <b>[속보]</b> {linked}\n\n"
        f"📌 <b>내용</b>\n{_s(summary)}\n\n"
        f"⚡ <b>시장 영향</b>\n{_s(impact)}\n\n"
        f"<i>출처: {_s(source)}</i>"
    )
