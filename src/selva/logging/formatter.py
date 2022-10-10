import importlib
import inspect
import json
import logging
from datetime import date, datetime, time
from logging import Formatter, LogRecord

try:
    importlib.import_module("colorama")
    COLORAMA = True
except ImportError:
    COLORAMA = False

if COLORAMA:
    import colorama
    from colorama import Fore, Style

    colorama.init(autoreset=True)

    LEVEL_COLOR = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def _format_log_date(record: LogRecord) -> str:
        log_date = datetime.fromtimestamp(record.created).isoformat(timespec="seconds")
        return f"{Fore.BLUE}{log_date}{Fore.RESET}"

    def _format_log_level(record: LogRecord) -> str:
        level_color = LEVEL_COLOR.get(record.levelno, "")
        return f"{level_color}{record.levelname:<8}{Fore.RESET + Style.RESET_ALL}"

    def _format_log_pair(key: str, value: str) -> str:
        return f"{Fore.CYAN}{key}{Fore.BLUE}={Fore.YELLOW}{value}{Fore.RESET}"

else:

    def _format_log_date(record: LogRecord) -> str:
        log_date = datetime.fromtimestamp(record.created).isoformat(timespec="seconds")
        return log_date

    def _format_log_level(record: LogRecord) -> str:
        return f"{record.levelname:<8}"

    def _format_log_pair(key: str, value: str) -> str:
        return f"{key}={value}"


class BaseFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, record: LogRecord) -> dict:
        context = getattr(record, "context", {})

        context = {
            "timestamp": datetime.fromtimestamp(record.created),
            "level": record.levelname,
            "source": record.name,
            "event": record.msg,
        } | context

        if record.exc_info:
            context["traceback"] = self.format_exception(record)

        return context

    def format_exception(self, record: LogRecord) -> str | None:
        if record.exc_info:
            return super().formatException(record.exc_info)

        return None

    def convert_value(self, value):
        if isinstance(value, str):
            result = repr(value) if " " in value else value
        elif isinstance(value, (int, float, bool)):
            result = value
        elif isinstance(value, (date, time, datetime)):
            result = value.isoformat()
        elif isinstance(value, type) or inspect.isfunction(value):
            result = f"{value.__module__}.{value.__qualname__}"
        else:
            result = repr(value)

        return result


class DevFormatter(BaseFormatter):
    def get_context(self, record: LogRecord) -> dict:
        context = getattr(record, "context", {})
        return context

    def convert_value(self, value):
        value = super().convert_value(value)
        if isinstance(value, str) and len(value) > 100:
            value = f"{value[:97]}..."
        return value

    def format(self, record: LogRecord) -> str:
        context = self.get_context(record)

        log_date = self._get_log_date(record)
        level = self._get_log_level(record)

        log_line = f"{log_date} | {level} | {record.msg}"

        if log_data := self._generate_log_data(context):
            log_line += " " + log_data

        if traceback := self.format_exception(record):
            log_line += "\n" + traceback

        return log_line

    @staticmethod
    def _get_log_date(record: LogRecord) -> str:
        return _format_log_date(record)

    @staticmethod
    def _get_log_level(record: LogRecord) -> str:
        return _format_log_level(record)

    def _generate_log_data(self, context: dict) -> str:
        data = []

        for key, value in context.items():
            value = self.convert_value(value)
            data.append(_format_log_pair(key, value))

        return " ".join(data)


class KeyValueFormatter(BaseFormatter):
    def format(self, record: LogRecord) -> str:
        context = self.get_context(record)

        log_ctx = []
        for key, value in context.items():
            log_ctx.append(f"{key}={self.convert_value(value)}")

        return " ".join(log_ctx)


class JsonFormatter(BaseFormatter):
    def convert_value(self, value):
        if isinstance(value, (str, int, float, bool)):
            result = value
        elif isinstance(value, (date, time, datetime)):
            result = value.isoformat()
        elif isinstance(value, type) or inspect.isfunction(value):
            result = f"{value.__module__}.{value.__qualname__}"
        else:
            result = repr(value)

        return result

    def format(self, record: LogRecord) -> str:
        context = self.get_context(record)

        result = {key: self.convert_value(value) for key, value in context.items()}

        return json.dumps(result)
