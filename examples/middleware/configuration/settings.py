from application.middlewares import TimingMiddleware, LoggingMiddleware, AuthMiddleware

SELVA__MIDDLEWARE_CLASSES = [
    TimingMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
]
