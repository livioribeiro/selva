import base64
from datetime import datetime
from http import HTTPStatus

import structlog
from asgikit.requests import Request
from asgikit.responses import respond_status

from .auth import User

logger = structlog.get_logger()


async def auth_middleware(callnext, request: Request):
    if request.path == "/protected":
        response = request.response
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

    await callnext(request)


async def timing_middleware(callnext, request: Request):
    if request.is_websocket:
        await callnext(request)
        return

    request_start = datetime.now()
    await callnext(request)
    request_end = datetime.now()

    delta = request_end - request_start
    logger.info("request duration", duration=str(delta))


async def logging_middleware(callnext, request: Request, user: User = None):
    logger.info("user", user=user.name if user else "<no user>")

    if request.is_websocket:
        await callnext(request)
        return

    await callnext(request)

    client = f"{request.client[0]}:{request.client[1]}"
    request_line = f"{request.method} {request.path} HTTP/{request.http_version}"
    status = request.response.status

    logger.info(
        "request",
        client=client,
        request_line=request_line,
        status=status.value,
        status_phrase=status.phrase,
    )
