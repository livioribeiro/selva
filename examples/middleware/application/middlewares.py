import base64
from datetime import datetime
from http import HTTPStatus

from selva.web import HttpResponse, RequestContext
from selva.web.middleware import Middleware


class TimingMiddleware(Middleware):
    order = 1

    async def execute(self, chain, context: RequestContext):
        request_start = datetime.now()
        response = await chain(context)
        request_end = datetime.now()

        delta = request_end - request_start
        print(f"Request time: {delta}")

        return response


class LoggingMiddleware(Middleware):
    order = 2

    async def execute(self, chain, context: RequestContext):
        response = await chain(context)

        client = f"{context.client[0]}:{context.client[1]}"
        request_line = (
            f"{context.method} {context.path} HTTP/{context.http_version}"
        )
        status = f"{response.status.value} {response.status.phrase}"

        print(f'{client} "{request_line}" {status}')

        return response


class AuthMiddleware(Middleware):
    async def execute(self, chain, context: RequestContext):
        if context.path == "/protected":
            authn = context.headers.get("authorization")
            if not authn:
                return HttpResponse(
                    status=HTTPStatus.UNAUTHORIZED,
                    headers={
                        "WWW-Authenticate": 'Basic realm="localhost:8000/protected"'
                    },
                )

            authn = authn.removeprefix("Basic")
            user, password = base64.urlsafe_b64decode(authn).decode().split(":")
            print(f"User '{user}' with password '{password}'")
            context["user"] = user

        return await chain(context)
