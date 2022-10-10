from application.middlewares import TimingMiddleware, LoggingMiddleware, AuthMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]

LOGGING_LOGGERS = {
    "selva": "DEBUG"
}

LOGGING_FORMATTER = "dev"
