import base64
from collections.abc import Awaitable, Callable
from datetime import datetime
from http import HTTPStatus

from selva.web import HttpResponse, RequestContext, middleware


@middleware
class LoggingMiddleware:
    async def execute(self, chain, context: RequestContext):
        response = await chain(context)

        print(
            f"{context.method} {context.path} {response.status.value} {response.status.phrase}"
        )

        return response


@middleware
class AuthMiddleware:
    async def execute(self, chain, context: RequestContext):
        if context.path != "/protected":
            return await chain(context)

        authn = context.headers.get("authorization")
        if not authn:
            return HttpResponse(
                status=HTTPStatus.UNAUTHORIZED,
                headers={"WWW-Authenticate": 'Basic realm="localhost:8000/protected"'},
            )

        authn = authn.removeprefix("Basic")
        user, password = base64.urlsafe_b64decode(authn).decode().split(":")
        print(f"User '{user}' with password '{password}'")

        context["user"] = user

        return await chain(context)


@middleware
class TimingMiddleware:
    async def execute(self, chain, context: RequestContext):
        request_start = datetime.now()

        response = await chain(context)

        request_end = datetime.now()

        delta = request_end - request_start
        print(f"Request time: {delta}")

        return response
