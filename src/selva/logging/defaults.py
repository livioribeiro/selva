LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "{asctime} {levelname:<8} {message}",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "style": "{",
        },
        "logfmt": {
            "()": "logfmter.Logfmter",
            "keys": ["timestamp", "level", "name", "event"],
            "mapping": {
                "timestamp": "asctime",
                "level": "levelname",
                "event": "message",
            },
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
