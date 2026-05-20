# In-memory store: {chat_id: interval_hours}
# Survives only while the process is running. Replace with DB for persistence.
_store: dict[int, int] = {}


def set_job(chat_id: int, interval_hours: int) -> None:
    _store[chat_id] = interval_hours


def get_job(chat_id: int) -> int | None:
    return _store.get(chat_id)


def remove_job(chat_id: int) -> None:
    _store.pop(chat_id, None)


def job_name(chat_id: int) -> str:
    return f"notif_{chat_id}"
