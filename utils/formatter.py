from html import escape


def _safe(text: str) -> str:
    return escape(str(text))


def _article_links(articles: list[dict], limit: int = 5) -> str:
    lines = []
    for a in articles[:limit]:
        title = _safe(a["title"][:65]) + ("…" if len(a["title"]) > 65 else "")
        link = a.get("link", "")
        source = _safe(a.get("source", ""))
        if link:
            lines.append(f'• <a href="{link}">{title}</a> <i>[{source}]</i>')
        else:
            lines.append(f"• {title} <i>[{source}]</i>")
    return "\n".join(lines)


def ai_report(summary: str, articles: list[dict]) -> str:
    links = _article_links(articles)
    return (
        "🤖 <b>AI 브리핑 리포트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{_safe(summary)}\n\n"
        "📎 <b>주요 참고 기사</b>\n"
        f"{links}"
    )


def semi_report(summary: str, articles: list[dict]) -> str:
    links = _article_links(articles)
    return (
        "💾 <b>반도체 브리핑 리포트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{_safe(summary)}\n\n"
        "📎 <b>주요 참고 기사</b>\n"
        f"{links}"
    )


def digest_report(ai_summary: str, semi_summary: str) -> str:
    return (
        "📬 <b>정기 뉴스 다이제스트</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 <b>AI 동향</b>\n"
        f"{_safe(ai_summary)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "💾 <b>반도체 동향</b>\n"
        f"{_safe(semi_summary)}"
    )


def breaking_news(title: str, features: str, impact: str) -> str:
    return (
        f"🚨 <b>[긴급 속보] {_safe(title)}</b>\n\n"
        f"🎯 <b>주요 내용</b>\n"
        f"{_safe(features)}\n\n"
        f"⚡ <b>시장 영향력</b>\n"
        f"{_safe(impact)}"
    )
