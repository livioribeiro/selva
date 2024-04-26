import json
import traceback

from . import _ensure_json


def formatter(record):
    extra = _ensure_json(record["extra"])

    message = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
    } | extra

    if exc := record.get("exception"):
        exc_type, exc_value, exc_traceback = exc
        tb = traceback.format_tb(exc_traceback)
        message["exception"] = tb

    record["message"] = json.dumps(message) + "\n"

    return "{message}"
