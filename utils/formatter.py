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


def digest_report(ai_summary: str, semi_summary: str) -> str:
    return (
        "📬 <b>정기 뉴스 다이제스트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>AI 동향</b>\n{_s(ai_summary)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💾 <b>반도체 동향</b>\n{_s(semi_summary)}"
    )


def breaking_news(title: str, features: str, impact: str) -> str:
    return (
        f"🚨 <b>[긴급 속보] {_s(title)}</b>\n\n"
        f"🎯 <b>주요 내용</b>\n{_s(features)}\n\n"
        f"⚡ <b>시장 영향력</b>\n{_s(impact)}"
    )
