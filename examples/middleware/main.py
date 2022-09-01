from selva.web import Selva

from application.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

app = Selva(
    middleware=[
        TimingMiddleware,
        LoggingMiddleware,
        AuthMiddleware,
    ]
)
