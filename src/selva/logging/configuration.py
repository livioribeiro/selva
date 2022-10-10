import logging.config
from copy import deepcopy

from selva.configuration.settings import Settings

_default_dict_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "dev": {
            "class": "selva.logging.formatter.DevFormatter",
        },
        "keyvalue": {
            "class": "selva.logging.formatter.KeyValueFormatter",
        },
        "json": {
            "class": "selva.logging.formatter.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "dev",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "NOTSET",
    },
    "loggers": {
        "selva": {
            "level": "WARNING",
        },
    },
}


def configure_logging(settings: Settings):
    if config := settings.get("LOGGING_CONFIG"):
        logging.config.dictConfig(config)
        return

    config = deepcopy(_default_dict_config)

    config["root"]["level"] = settings.LOGGING_LEVEL
    config["handlers"]["console"]["formatter"] = settings.LOGGING_FORMATTER

    loggers = settings.LOGGING_LOGGERS
    if not isinstance(loggers, dict):
        raise ValueError("LOGGING_LOGGERS must be a dict of {'name': 'level'}")

    config["loggers"] = {name: {"level": level} for name, level in loggers.items()}

    logging.config.dictConfig(config)
