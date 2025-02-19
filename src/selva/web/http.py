from functools import singledispatchmethod
from http import HTTPMethod, HTTPStatus
from os import PathLike

from starlette.requests import Request as BaseRequest
from starlette.responses import (
    Response,
    HTMLResponse,
    PlainTextResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
    FileResponse,
)
from starlette.types import Scope, Receive, Send
from starlette.websockets import WebSocket


__all__ = (
    "Request",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "RedirectResponse",
    "StreamingResponse",
    "FileResponse",
    "WebSocket",
)


class Request(BaseRequest):
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope, receive, send)
        self.__receive = receive
        self.__send = send
        self.scope["__finished__"] = False

    @property
    def method(self) -> HTTPMethod:
        return HTTPMethod(super().method)

    @singledispatchmethod
    async def respond(self, response: Response):
        await response(self.scope, self.__receive, self.__send)
        self.scope["__finished__"] = True

    @respond.register
    async def _(self, response: str):
        await self.respond(PlainTextResponse(response))

    @respond.register(list)
    @respond.register(dict)
    async def _(self, response: list | dict):
        await self.respond(JSONResponse(response))

    @respond.register
    async def _(self, response: PathLike):
        await self.respond(FileResponse(response))

    @respond.register
    async def _(self, response: HTTPStatus):
        await self.respond(Response(status_code=response))
