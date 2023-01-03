from selva.configuration.environment import get_dict

COMPONENTS = []

MIDDLEWARE = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} {levelname:<8} {name}[{threadName}] {message}",
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
        "application": {
            "level": "WARNING",
            "handlers": ["console"],
        },
        "selva": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    },
}

LOGGING_LEVEL = get_dict("LOG_LEVEL", {})
