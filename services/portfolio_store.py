import json
import logging
import os

logger = logging.getLogger(__name__)

_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.json")
_store: dict[str, list[dict]] = {}


def _load() -> None:
    global _store
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            _store = json.load(f)
    except FileNotFoundError:
        _store = {}
    except Exception as e:
        logger.warning("portfolio load error: %s", e)
        _store = {}


def _save() -> None:
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(_store, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("portfolio save error: %s", e)


_load()


def _key(chat_id: int) -> str:
    return str(chat_id)


def get_portfolio(chat_id: int) -> list[dict]:
    return _store.get(_key(chat_id), [])


def add_position(chat_id: int, ticker: str, name: str, qty: int, avg_price: int) -> str:
    """이미 있으면 평단 재계산. 반환값: 'added' | 'updated'"""
    positions = _store.setdefault(_key(chat_id), [])
    for pos in positions:
        if pos["ticker"] == ticker:
            total_qty = pos["qty"] + qty
            pos["avg_price"] = round(
                (pos["avg_price"] * pos["qty"] + avg_price * qty) / total_qty
            )
            pos["qty"] = total_qty
            _save()
            return "updated"
    positions.append({"ticker": ticker, "name": name, "qty": qty, "avg_price": avg_price})
    _save()
    return "added"


def remove_position(chat_id: int, ticker: str) -> bool:
    positions = _store.get(_key(chat_id), [])
    before = len(positions)
    _store[_key(chat_id)] = [p for p in positions if p["ticker"] != ticker]
    _save()
    return len(_store[_key(chat_id)]) < before
