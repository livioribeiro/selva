import logging
import logging.config
import sys

import structlog

from selva.configuration.settings import Settings


def setup(settings: Settings):
    structlog.configure(
        processors=[structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    log_format = settings.logging.get("format")
    if not log_format:
        log_format = "console" if sys.stderr.isatty() else "json"

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    elif log_format == "logfmt":
        renderer = structlog.processors.LogfmtRenderer(bool_as_flag=False)
    elif log_format == "keyvalue":
        renderer = structlog.processors.KeyValueRenderer()
    elif log_format == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        raise ValueError("Unknown log format")

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    ]

    if not isinstance(renderer, structlog.dev.ConsoleRenderer):
        processors.append(structlog.processors.dict_tracebacks)

    processors.append(renderer)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "structlog": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": processors,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structlog",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": settings.logging.get("root", "INFO").upper(),
        },
        "loggers": {
            module: {"level": level.upper()}
            for module, level in settings.logging.get("level", {}).items()
        },
    }

    logging.config.dictConfig(logging_config)
