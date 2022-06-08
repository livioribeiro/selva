from selva.web import Application

from . import module
from .module.middlewares import AuthMiddleware, LoggingMiddleware, TimingMiddleware

app = Application()
app.register(TimingMiddleware, LoggingMiddleware, AuthMiddleware, module)
