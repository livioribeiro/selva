import logging
import logging.config
import sys

import structlog

from selva.conf.settings import Settings


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

    root_level = settings.logging.get("root", "WARN").upper()

    extra_loggers = {
        "sqlalchemy.engine.Engine": {
            "level": root_level,
            "handlers": ["console"],
        },
        "uvicorn": {
            "level": root_level,
            "handlers": ["console"],
        },
        "_granian": {
            "level": root_level,
            "handlers": ["console"],
        },
        "granian.access": {
            "level": root_level,
            "handlers": ["console"],
        },
    }

    loggers = {
        module: {"level": level.upper(), "handlers": ["console"], "propagate": False}
        for module, level in settings.logging.get("level", {}).items()
    }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
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
            "level": root_level,
        },
        "loggers": extra_loggers | loggers,
    }

    logging.config.dictConfig(logging_config)
