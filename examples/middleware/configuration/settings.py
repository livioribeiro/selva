from application.middleware import AuthMiddleware, LoggingMiddleware, TimingMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]

LOGGING_LEVEL = {
    "application": "INFO",
    "selva": "INFO",
}
