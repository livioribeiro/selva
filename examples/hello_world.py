import base64
import os
from collections.abc import Callable
from http import HTTPStatus
from typing import NamedTuple

from asgikit.responses import HttpResponse, PlainTextResponse

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
    def index(self, context: RequestContext) -> PlainTextResponse:
        name = context.query.get("name")
        greeting = self.greeter.greet(name)
        user = context["user"]
        return PlainTextResponse(f"{greeting} (from {user})")

    @get("/logout")
    def logout(self):
        return HttpResponse(
            status=HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": 'Basic realm="localhost:8000"'},
        )


@middleware
class LoggingMiddleware:
    async def __call__(self, context: RequestContext, chain: Callable):
        response = await chain()
        print(
            f"{context.method} {context.path} {response.status.value} {response.status.phrase}"
        )
        return response


@middleware
class AuthMiddleware:
    async def __call__(self, context: RequestContext, chain: Callable):
        authn = context.headers.get("authorization")
        if not authn:
            return HttpResponse(
                status=HTTPStatus.UNAUTHORIZED,
                headers={"WWW-Authenticate": 'Basic realm="localhost:8000"'},
            )

        authn = authn.removeprefix("Basic")
        user, password = base64.urlsafe_b64decode(authn).decode().split(":")
        print(f"User '{user}' with password '{password}'")

        context["user"] = user
        return await chain()


app = Application()
app.register(Controller, LoggingMiddleware, AuthMiddleware, settings_factory, Greeter)
