import os
from collections.abc import Callable
from typing import NamedTuple

from asgikit.requests import HttpRequest
from asgikit.responses import PlainTextResponse

from selva.di import service
from selva.web import Application, controller, get, middleware
from selva.web.request import RequestContext

DEFAULT_NAME = "World"


class Settings(NamedTuple):
    default_name: str


@service
def settings_factory() -> Settings:
    default_name = os.getenv("DEFAULT_NAME", DEFAULT_NAME)
    return Settings(default_name)


@service
class Greeter:
    def __init__(self, settings: Settings):
        self.default_name = settings.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}"


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get
    def index(self, req: HttpRequest) -> PlainTextResponse:
        name = req.query.get_first("name")
        greeting = self.greeter.greet(name)
        return PlainTextResponse(greeting)


@middleware
async def logging_middleware(context: RequestContext, chain: Callable):
    print(context.path)
    response = await chain()
    print(f"status: {response.status.value}")
    return response


@middleware
class AuthMiddleware:
    async def __call__(self, context: RequestContext, chain: Callable):
        print("AuthMiddleware")
        return await chain()


app = Application()
app.register(Controller, logging_middleware, AuthMiddleware, settings_factory, Greeter)
