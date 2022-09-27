from application.middlewares import TimingMiddleware, LoggingMiddleware, AuthMiddleware

MIDDLEWARE = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]
