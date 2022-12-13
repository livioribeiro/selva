from application.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]

LOGGING_LOGGERS = {"selva": "INFO"}

LOGGING_FORMATTER = "dev"
