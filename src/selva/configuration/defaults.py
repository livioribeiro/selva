import os

DEBUG = os.getenv("SELVA_DEBUG", "False") in ("1", "True")

COMPONENTS = []

MIDDLEWARE = []

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG" if DEBUG else "WARNING")
LOGGING_LOGGERS = {
    "selva": "DEBUG" if DEBUG else "WARNING",
}

LOGGING_FORMATTER = "dev" if DEBUG else "json"
