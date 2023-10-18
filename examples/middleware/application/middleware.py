import base64
import logging
from datetime import datetime
from http import HTTPStatus

from asgikit.requests import Request
from asgikit.responses import Response, respond_status

from selva.web.middleware import Middleware

logger = logging.getLogger(__name__)


class TimingMiddleware(Middleware):
    async def __call__(self, chain, request: Request, response: Response):
        if request.is_websocket:
            await chain(request, response)
            return

        request_start = datetime.now()
        await chain(request, response)
        request_end = datetime.now()

        delta = request_end - request_start
        logging.warning("Request time: %s", delta)


class LoggingMiddleware(Middleware):
    async def __call__(self, chain, request: Request, response: Response):
        if request.is_websocket:
            await chain(request, response)
            return

        await chain(request, response)

        client = f"{request.client[0]}:{request.client[1]}"
        request_line = f"{request.method} {request.path} HTTP/{request.http_version}"
        status = response.status

        logging.warning('%s "%s" %s %s', client, request_line, status.value, status.phrase)


class AuthMiddleware(Middleware):
    async def __call__(self, chain, request: Request, response: Response):
        if request.path == "/protected":
            authn = request.headers.get("authorization")
            if not authn:
                response.header("WWW-Authenticate", 'Basic realm="localhost:8000/protected"')
                await respond_status(response, HTTPStatus.UNAUTHORIZED)
                return

            authn = authn.removeprefix("Basic")
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            logging.info(f"User '%s' with password '%s'", user, password)
            request["user"] = user

        await chain(request, response)
