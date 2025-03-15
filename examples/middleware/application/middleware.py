import base64
from datetime import datetime
from http import HTTPStatus
from urllib.parse import unquote_plus

import structlog

from selva.web import Request

logger = structlog.get_logger()


def auth_middleware(app, settings, di):
    auth_user = settings.auth.username
    auth_pass = settings.auth.password

    async def func(scope, receive, send):
        if scope["path"] == "/protected":
            request = Request(scope, receive, send)
            authn = request.headers.get("authorization")

            if not authn:
                await request.respond(
                    HTTPStatus.UNAUTHORIZED,
                    headers={
                        "WWW-Authenticate": 'Basic realm="localhost:8000/protected"'
                    },
                )
                return

            authn = authn.removeprefix("Basic").strip()
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            if not (user == auth_user and password == auth_pass):
                await request.respond(HTTPStatus.UNAUTHORIZED)
                return

            logger.info("user logged in", user=user, password=password)
            scope["user"] = user

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

        await app(scope, receive, send)

        if scope["type"] == "websocket":
            return

        client = f"{scope['client'][0]}:{scope['client'][1]}"
        query_string = ""
        if qs := scope.get("query_string"):
            query_string = "?" + unquote_plus(qs.decode())
        request_line = f"{scope['method']} {scope['path']}{query_string} HTTP/{scope['http_version']}"
        status = scope["__response__"]["status_code"]

        logger.info(
            "request",
            client=client,
            request_line=request_line,
            status_code=status.value,
            status_phrase=status.phrase,
        )

    return func
