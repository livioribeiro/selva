import os

DEBUG = os.getenv("SELVA_DEBUG", "false").lower() in ("1", "true")

COMPONENTS = []

MIDDLEWARE = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} | {levelname:<8} | {name} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "selva": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "application": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}
