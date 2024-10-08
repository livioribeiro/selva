import base64
from datetime import datetime
from http import HTTPStatus

from asgikit.requests import Request
from asgikit.responses import respond_status

import structlog

from selva.web.middleware import Middleware

logger = structlog.get_logger()


class TimingMiddleware(Middleware):
    async def __call__(self, chain, request: Request):
        if request.is_websocket:
            await chain(request)
            return

        request_start = datetime.now()
        await chain(request)
        request_end = datetime.now()

        delta = request_end - request_start
        logger.info("request duration", duration=str(delta))


class LoggingMiddleware(Middleware):
    async def __call__(self, chain, request: Request):
        if request.is_websocket:
            await chain(request)
            return

        await chain(request)

        client = f"{request.client[0]}:{request.client[1]}"
        request_line = f"{request.method} {request.path} HTTP/{request.http_version}"
        status = request.response.status

        logger.info("request", client=client, request_line=request_line, status=status.value, status_phrase=status.phrase)


class AuthMiddleware(Middleware):
    async def __call__(self, chain, request: Request):
        response = request.response
        if request.path == "/protected":
            authn = request.headers.get("authorization")
            if not authn:
                response.header(
                    "WWW-Authenticate", 'Basic realm="localhost:8000/protected"'
                )
                await respond_status(response, HTTPStatus.UNAUTHORIZED)
                return

            authn = authn.removeprefix("Basic")
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            logger.info("user logged in", user=user, password=password)
            request["user"] = user

        await chain(request)
