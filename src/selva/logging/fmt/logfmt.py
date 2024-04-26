import json
import string
import traceback
from functools import lru_cache

from . import _ensure_json


LOG_FORMAT = "timestamp={time:%Y-%m-%dT%H:%M:%S} level={level} message={message}"


def _normalize_name(name: str) -> str:
    for char in string.whitespace:
        name = name.replace(char, "_").strip()
    return name


@lru_cache(maxsize=128)
def _log_format(*args: str):
    return " ".join(f"{_normalize_name(name)}={{extra[{name}]}}" for name in args)


def formatter(record):
    record["message"] = json.dumps(record["message"])

    extra = _ensure_json(record["extra"])
    for key, val in extra.items():
        if (
            isinstance(val, (dict, bool))
            or (isinstance(val, str) and any(i for i in string.whitespace if i in val))
        ):
            record["extra"][key] = json.dumps(val)

    extra_keys = record["extra"].keys()
    extra_format = _log_format(*extra_keys)
    log_format = f"{LOG_FORMAT} {extra_format}"

    if exc := record.get("exception"):
        exc_type, exc_value, exc_traceback = exc
        tb = traceback.format_tb(exc_traceback)
        record["extra"]["exception"] = json.dumps("".join(tb))
        log_format = f"{log_format} exception={{extra[exception]}}"

    return log_format + "\n"
