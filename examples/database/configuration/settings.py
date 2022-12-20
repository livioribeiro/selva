DATABASE_URL = "sqlite:///database.sqlite3"

LOGGING_LOGGERS = {
    "selva": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "application": {
        "handlers": ["console"],
        "level": "INFO",
    },
}