import base64
from datetime import datetime
from http import HTTPStatus

from selva.di import service
from selva.web.contexts import RequestContext
from selva.web.middleware import Middleware

from selva.web.responses import Response


@service
class TimingMiddleware(Middleware):
    async def __call__(self, context: RequestContext, chain):
        if context.is_websocket:
            return await chain(context)

        request_start = datetime.now()
        response = await chain(context)
        request_end = datetime.now()

        delta = request_end - request_start
        print(f"Request time: {delta}")

        return response


@service
class LoggingMiddleware(Middleware):
    async def __call__(self, context: RequestContext, chain):
        if context.is_websocket:
            await chain(context)

        response = await chain(context)

        client = f"{context.client[0]}:{context.client[1]}"
        request_line = f"{context.method} {context.path} HTTP/{context['http_version']}"
        status = HTTPStatus(response.status_code)
        status = f"{status.value} {status.phrase}"

        print(f'{client} "{request_line}" {status}')

        return response


@service
class AuthMiddleware(Middleware):
    async def __call__(self, context: RequestContext, chain):
        if context.path == "/protected":
            authn = context.headers.get("authorization")
            if not authn:
                return Response(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    headers={
                        "WWW-Authenticate": 'Basic realm="localhost:8000/protected"'
                    },
                )

            authn = authn.removeprefix("Basic")
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            print(f"User '{user}' with password '{password}'")
            context["user"] = user

        return await chain(context)
