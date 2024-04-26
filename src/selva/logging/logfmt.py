import json
import string
import traceback
from functools import lru_cache


LOG_FORMAT = (
    "<yellow>timestamp</yellow><white>=</white><light-green>{time:%Y-%m-%dT%H:%M:%S}</light-green>"
    " <yellow>level</yellow><white>=</white><level>{level}</level>"
    " <yellow>message</yellow><white>=</white><level>{message}</level>"
)


@lru_cache(maxsize=128)
def _log_format(*args: str):
    return " ".join(
        (
            f"<cyan>{name}</cyan><white>=</white>"
            "<light-blue>{extra[" + name + "]}</light-blue>"
        )
        for name in args
    )


def formatter(record):
    record["message"] = json.dumps(record["message"])

    for key, val in record["extra"].items():
        serialized = str(val)
        if any(i for i in string.whitespace if i in serialized):
            serialized = json.dumps(val)

        record["extra"][key] = serialized

    extra_format = _log_format(*record["extra"].keys())

    log_format = LOG_FORMAT

    if exc := record.get("exception"):
        exc_type, exc_value, exc_traceback = exc
        tb = traceback.format_tb(exc_traceback)
        record["extra"]["exception"] = json.dumps("".join(tb).strip())
        log_format = f"{log_format} <yellow>exception</yellow><white>=</white><level>" "{extra[exception]}</level>"

    return f"{log_format} {extra_format}"
