import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-X700) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.stock.naver.com/",
    "Accept": "application/json",
}
_TIMEOUT = 10


def _n(val, default="—") -> str:
    if val is None or str(val).strip() == "":
        return default
    return str(val).strip()


def _sign(compare_obj: dict) -> str:
    name = compare_obj.get("name", "") if compare_obj else ""
    if name == "RISING":
        return "▲"
    if name == "FALLING":
        return "▼"
    return ""


def _info_map(total_infos: list) -> dict[str, str]:
    """totalInfos 리스트 → {code: value} 맵"""
    return {item["code"]: item.get("value", "") for item in total_infos if "code" in item}


def _strip_unit(val: str) -> str:
    """'29.14배', '12,372원' 등에서 단위 제거"""
    return val.replace("배", "").replace("원", "").replace("%", "").strip()


# ── 종목 검색 ──────────────────────────────────────────────────────────────

def _search_sync(query: str) -> list[dict]:
    resp = httpx.get(
        "https://ac.finance.naver.com/api/search",
        params={"q": query, "target": "stock,index"},
        headers=_HEADERS,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [[]])[0]
    return [{"ticker": item[1], "name": item[0]} for item in items if len(item) >= 2]


async def search_ticker(query: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _search_sync, query)


# ── 현재가 + 재무지표 ──────────────────────────────────────────────────────

def _get_price_sync(ticker: str) -> dict:
    # basic: 현재가·등락
    basic = httpx.get(
        f"https://m.stock.naver.com/api/stock/{ticker}/basic",
        headers=_HEADERS, timeout=_TIMEOUT,
    ).json()

    # integration: OHLC·거래량·PER/PBR·시총 등
    integ = httpx.get(
        f"https://m.stock.naver.com/api/stock/{ticker}/integration",
        headers=_HEADERS, timeout=_TIMEOUT,
    ).json()

    inf = _info_map(integ.get("totalInfos", []))

    sign_obj = basic.get("compareToPreviousPrice", {})

    return {
        "ticker": ticker,
        "name": _n(basic.get("stockName"), ticker),
        "price": _n(basic.get("closePrice")),
        "change": _n(basic.get("compareToPreviousClosePrice")),
        "change_rate": _n(basic.get("fluctuationsRatio")),
        "sign": _sign(sign_obj),
        "open": _n(inf.get("openPrice")),
        "high": _n(inf.get("highPrice")),
        "low": _n(inf.get("lowPrice")),
        "volume": _n(inf.get("accumulatedTradingVolume")),
        "trade_value": _n(inf.get("accumulatedTradingValue")),
        "market_cap": _n(inf.get("marketValue")),
        "foreign_rate": _n(inf.get("foreignRate")),
        "w52_high": _n(inf.get("highPriceOf52Weeks")),
        "w52_low": _n(inf.get("lowPriceOf52Weeks")),
        "per": _strip_unit(_n(inf.get("per"))),
        "eps": _strip_unit(_n(inf.get("eps"))),
        "pbr": _strip_unit(_n(inf.get("pbr"))),
        "bps": _strip_unit(_n(inf.get("bps"))),
        "per_fwd": _strip_unit(_n(inf.get("cnsPer"))),   # 추정 PER
        "dividend_yield": _n(inf.get("dividendYieldRatio")),
    }


def _get_financial_sync(ticker: str) -> dict:
    """재무비율 (ROE, 부채비율 등) — 실패해도 빈 dict 반환"""
    try:
        resp = httpx.get(
            f"https://m.stock.naver.com/api/stock/{ticker}/finance/ratio",
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json().get("financeRatioItems", [])
        if not items:
            return {}
        latest = items[0]
        return {
            "period": _n(latest.get("stacYymm")),
            "roe": _n(latest.get("roe")),
            "debt_ratio": _n(latest.get("lbltRate")),
            "operating_margin": _n(latest.get("bsopPrfiInrt")),
            "net_margin": _n(latest.get("ntinInrt")),
        }
    except Exception as e:
        logger.debug("financial fetch failed for %s: %s", ticker, e)
        return {}


async def get_price(ticker: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_price_sync, ticker)


async def get_financial(ticker: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_financial_sync, ticker)


# ── 지수 ──────────────────────────────────────────────────────────────────

def _get_index_sync(code: str) -> dict:
    resp = httpx.get(
        f"https://m.stock.naver.com/api/index/{code}/basic",
        headers=_HEADERS, timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    d = resp.json()
    return {
        "name": code,
        "price": _n(d.get("closePrice")),
        "change": _n(d.get("compareToPreviousClosePrice")),
        "change_rate": _n(d.get("fluctuationsRatio")),
        "sign": _sign(d.get("compareToPreviousPrice", {})),
    }


async def get_market_overview(watchlist: dict[str, str]) -> dict:
    loop = asyncio.get_event_loop()

    kospi_fut  = loop.run_in_executor(None, _get_index_sync, "KOSPI")
    kosdaq_fut = loop.run_in_executor(None, _get_index_sync, "KOSDAQ")
    stock_futs = {t: loop.run_in_executor(None, _get_price_sync, t) for t in watchlist}

    kospi  = await kospi_fut
    kosdaq = await kosdaq_fut

    stocks: dict[str, dict] = {}
    for ticker, fut in stock_futs.items():
        try:
            stocks[ticker] = await fut
        except Exception as e:
            logger.warning("market_overview %s 실패: %s", ticker, e)

    return {"kospi": kospi, "kosdaq": kosdaq, "stocks": stocks}
