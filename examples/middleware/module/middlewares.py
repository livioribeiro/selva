import base64
from datetime import datetime
from http import HTTPStatus

from selva.web import HttpResponse, RequestContext, middleware


@middleware
class LoggingMiddleware:
    def process_response(self, context: RequestContext, response: HttpResponse):
        print(
            f"{context.method} {context.path} {response.status.value} {response.status.phrase}"
        )
        return response


@middleware
class AuthMiddleware:
    def process_request(self, context: RequestContext):
        if context.path != "/protected":
            return

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

        return None


@middleware
class TimingMiddleware:
    def process_request(self, context: RequestContext):
        context["request_start"] = datetime.now()

    def process_response(self, context: RequestContext, _result):
        request_end = datetime.now()
        delta = request_end - context["request_start"]
        print(f"Request time: {delta}")
