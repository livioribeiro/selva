import base64
from datetime import datetime
from http import HTTPStatus

import structlog
from asgikit.requests import Request
from asgikit.responses import respond_status

logger = structlog.get_logger()


def auth_middleware(app, settings, di):
    auth_user = settings.auth.username
    auth_pass = settings.auth.password

    async def func(scope, receive, send):
        if scope["path"] == "/protected":
            request = Request(scope, receive, send)
            authn = request.headers.get("authorization")

            if not authn:
                request.response.header(
                    "WWW-Authenticate", 'Basic realm="localhost:8000/protected"'
                )
                await respond_status(request.response, HTTPStatus.UNAUTHORIZED)
                return

            authn = authn.removeprefix("Basic").strip()
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            if not (user == auth_user and password == auth_pass):
                await respond_status(request.response, HTTPStatus.UNAUTHORIZED)
                return

            logger.info("user logged in", user=user, password=password)
            request["user"] = user

        await app(scope, receive, send)

    return func


def timing_middleware(app, settings, di):
    async def func(scope, receive, send):
        if scope["type"] == "websocket":
            await app(scope, receive, send)
            return

        request_start = datetime.now()
        await app(scope, receive, send)
        request_end = datetime.now()

        delta = request_end - request_start
        logger.info("request duration", duration=str(delta))

    return func


def logging_middleware(app, settings, di):
    async def func(scope, receive, send):
        if user := scope.get("user"):
            logger.info("user", user=user.name)

        if scope["type"] == "websocket":
            await app(scope, receive, send)
            return

        await app(scope, receive, send)

        request = Request(scope, receive, send)
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

    return func
