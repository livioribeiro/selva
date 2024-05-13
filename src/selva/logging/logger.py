import asyncio
import datetime
import functools
import inspect
import json
import logging
import string
import sys
import threading
import traceback
from collections.abc import Callable
from enum import IntEnum
from functools import cached_property
from typing import Any, TypeAlias

TRACE = 5

logging.addLevelName(TRACE, "trace")

logging.getLevelNamesMapping()

LogEvent: TypeAlias = str | tuple[str, list]


class LogLevel(IntEnum):
    NOTSET = logging.NOTSET
    TRACE = TRACE
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogRecord:
    def __init__(
        self,
        level: LogLevel,
        logger_name: str,
        event: LogEvent,
        context: dict,
        exception: BaseException = None,
        timestamp: datetime.datetime = None,
    ):
        self.timestamp = timestamp or datetime.datetime.now()
        self.log_level = level
        self.log_logger = logger_name
        self.log_context = context
        self.log_event = event
        self.exception = exception

    @cached_property
    def event(self):
        return self.format_event(self.log_event, self.log_context)

    @staticmethod
    def format_event(event: LogEvent, context: dict) -> str:
        match event:
            case event if isinstance(event, str):
                return event.format(**context)
            case (event, *args) if isinstance(event, str):
                return event.format(*args, **context)
            case _:
                raise ValueError("Invalid event")


def _normalize_name(name: str) -> str:
    for char in string.whitespace:
        name = name.replace(char, "_").strip()
    return name


def _normalize_value(value: Any, depth=0):
    if depth == 0:
        if isinstance(value, bool) and depth == 0:
            return "true" if value else "false"

        if isinstance(value, str) and depth == 0:
            return json.dumps(value)

        if isinstance(value, (list, tuple, set, frozenset)):
            return json.dumps([_normalize_value(v, depth + 1) for v in value])

        if isinstance(value, dict):
            return json.dumps(
                {k: _normalize_value(v, depth + 1) for k, v in value.items()}
            )

    if isinstance(value, (str, int, float, bool)):
        return value

    return repr(value)


def _formatter(record: LogRecord) -> str:
    message = json.dumps(record.event)
    context = " ".join(
        f"{_normalize_name(name)}={_normalize_value(value)}"
        for name, value in record.log_context.items()
    )
    return f"{record.timestamp.isoformat()} {record.log_level:<8} {message} {context}"


class PrintHandler:
    def __init__(self, formatter: Callable[[LogRecord], str] = _formatter):
        self.formatter = formatter

    def __call__(self, record: LogRecord):
        message = self.formatter(record)
        print(message, file=sys.stderr)


class Logger:
    def __init__(self):
        self.root_level = LogLevel.INFO
        self.level_spec = {}
        self.handler = PrintHandler()

    def log(self, level: LogLevel, event: LogEvent, **kwargs):
        # if level < self.level:
        #     return

        name = inspect.currentframe().f_globals.get("__name__")
        record = LogRecord(level, name, event, kwargs)
        self.queue.put_nowait(record)
        # message = _formatter(record)

        # logger = logging.getLogger(name)
        # logger.log(level, message)

        # self.handler(record)

    def trace(self, event: LogEvent, **kwargs):
        self.log(LogLevel.TRACE, event, **kwargs)

    def debug(self, event: LogEvent, **kwargs):
        self.log(LogLevel.DEBUG, event, **kwargs)

    def info(self, event: LogEvent, **kwargs):
        self.log(LogLevel.INFO, event, **kwargs)

    def warning(self, event: LogEvent, **kwargs):
        self.log(LogLevel.WARNING, event, **kwargs)

    def error(self, event: LogEvent, **kwargs):
        self.log(LogLevel.ERROR, event, **kwargs)

    def exception(self, event: LogEvent | BaseException, *, exception=None, **kwargs):
        if isinstance(event, BaseException):
            exception = event
            event = str(event)

        if exception or (exception := sys.exception()):
            kwargs["exception"] = "".join(traceback.format_exception(exception)).rstrip(
                "\n"
            )

        self.log(LogLevel.ERROR, event, **kwargs)

    def critical(self, event: LogEvent, **kwargs):
        self.log(LogLevel.CRITICAL, event, **kwargs)

    # @overload
    # def log(self, record: LogRecord, call_level=0):
    #     if call_level:
    #         frame = inspect.currentframe()
    #         while call_level:
    #             frame = frame.f_back
    #             call_level -= 1
    #         record.name = frame.f_globals.get("__name__")
    #
    #     self.handler(record)


if __name__ == "__main__":
    logger = Logger()
    logger.info("logger")
    import time

    time.sleep(2)
