from application.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]

LOGGING_LEVEL = {
    "application": "DEBUG",
    "selva": "INFO",
}
