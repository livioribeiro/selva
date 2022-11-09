import logging
from types import TracebackType


class Logger:
    def __init__(self, name: str):
        self._inner = logging.getLogger(name)

    @property
    def name(self):
        return self._inner.name

    def log(self, level: int, msg: str, *, stdlog_kwargs: dict = None, **kwargs):
        stdlog_kwargs = stdlog_kwargs or {}
        extra = {"context": kwargs} | stdlog_kwargs.pop("extra", {})
        self._inner.log(level, msg, extra=extra, **stdlog_kwargs)

    def debug(self, msg: str, **kwargs):
        return self.log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        return self.log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        return self.log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        return self.log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        return self.log(logging.CRITICAL, msg, **kwargs)

    def exception(
        self,
        msg: str,
        *,
        exc_info: BaseException | tuple[BaseException, TracebackType] | bool = None,
        **kwargs,
    ):
        stdlog_kwargs = kwargs.pop("stdlogs_kwargs", {})
        stdlog_kwargs |= dict(exc_info=exc_info or True)
        return self.error(msg, stdlog_kwargs=stdlog_kwargs, **kwargs)
