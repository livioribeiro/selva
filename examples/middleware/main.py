from selva.web import Application

from .application.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

app = Application(
    middleware=[
        TimingMiddleware,
        LoggingMiddleware,
        AuthMiddleware,
    ]
)
