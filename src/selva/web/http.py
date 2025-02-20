import typing
import os
from functools import singledispatchmethod
from http import HTTPMethod, HTTPStatus

from starlette.datastructures import URL
from starlette.requests import Request as BaseRequest
from starlette.responses import (
    ContentStream,
    Response as BaseResponse,
    HTMLResponse as BaseHTMLResponse,
    PlainTextResponse as BasePlainTextResponse,
    JSONResponse as BaseJSONResponse,
    RedirectResponse as BaseRedirectResponse,
    StreamingResponse as BaseStreamingResponse,
    FileResponse as BaseFileResponse,
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


class Response(BaseResponse):
    def __init__(
        self,
        content: typing.Any = None,
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
    ):
        super().__init__(content, status_code=status, headers=headers, media_type=content_type)


class HTMLResponse(BaseHTMLResponse):
    def __init__(
        self,
        content: typing.Any = None,
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
    ):
        super().__init__(content, status_code=status, headers=headers, media_type=content_type)


class PlainTextResponse(BasePlainTextResponse):
    def __init__(
        self,
        content: str = None,
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
    ):
        super().__init__(content, status_code=status, headers=headers, media_type=content_type)


class JSONResponse(BaseJSONResponse):
    def __init__(
            self,
            content: typing.Any = None,
            status: HTTPStatus = HTTPStatus.OK,
            headers: dict[str, str] | None = None,
            content_type: str | None = None,
    ):
        super().__init__(content, status_code=status, headers=headers, media_type=content_type)


class RedirectResponse(BaseRedirectResponse):
    def __init__(
        self,
        url: str | URL,
        status: HTTPStatus = HTTPStatus.TEMPORARY_REDIRECT,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(url, status_code=status, headers=headers)


class StreamingResponse(BaseStreamingResponse):
    def __init__(
        self,
        content: ContentStream,
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
    ):
        super().__init__(content, status_code=status, headers=headers, media_type=content_type)


class FileResponse(BaseFileResponse):
    def __init__(
        self,
        path: str | os.PathLike[str],
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
        filename: str | None = None,
        stat_result: os.stat_result | None = None,
        method: str | None = None,
        content_disposition_type: str = "attachment",
    ):
        super().__init__(
            path,
            status_code=status,
            headers=headers,
            media_type=content_type,
            filename=filename,
            stat_result=stat_result,
            method=method,
            content_disposition_type=content_disposition_type
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
    async def _(self, response: os.PathLike):
        await self.respond(FileResponse(response))

    @respond.register
    async def _(self, response: HTTPStatus):
        await self.respond(Response(status=response))
