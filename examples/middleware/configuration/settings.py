from application.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]

LOGGING_LOGGERS = {"selva": "DEBUG"}

LOGGING_FORMATTER = "dev"
