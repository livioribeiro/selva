import os
from functools import singledispatchmethod, cached_property
from http import HTTPMethod, HTTPStatus

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

    @cached_property
    def method(self) -> HTTPMethod:
        return HTTPMethod(super().method)

    @singledispatchmethod
    async def respond(self, response: Response):
        await response(self.scope, self.__receive, self.__send)
        self.scope["__finished__"] = True
        self.scope["__response__"] = {
            "status_code": response.status_code,
        }

    @respond.register
    async def _(
        self,
        response: str,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
    ):
        await self.respond(
            PlainTextResponse(
                response,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
            )
        )

    @respond.register
    async def _(
        self,
        response: list | dict,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
    ):
        await self.respond(
            JSONResponse(
                response,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
            )
        )

    @respond.register
    async def _(
        self,
        response: os.PathLike,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
    ):
        await self.respond(
            FileResponse(
                response,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
            )
        )

    @respond.register
    async def _(
        self,
        response: HTTPStatus,
        headers: dict[str, str] | None = None,
    ):
        await self.respond(Response(status_code=response, headers=headers))
