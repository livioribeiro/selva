import os

DEBUG = os.getenv("SELVA_DEBUG", "false").lower() in ("1", "true")

COMPONENTS = []

MIDDLEWARE = []

LOGGING = None

LOGGING_FORMATTERS = {
    "default": {
        "format": "{asctime} {levelname:<8} {name}[{threadName}] {message}",
        "style": "{",
    },
}

LOGGING_HANDLERS = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "default",
    },
}

LOGGING_LOGGERS = {
    "selva": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "application": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
