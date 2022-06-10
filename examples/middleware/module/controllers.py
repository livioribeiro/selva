from http import HTTPStatus

from selva.web import HttpResponse, RequestContext, controller, get

from .services import Greeter


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get
    async def index(self, context: RequestContext):
        name = context.query.get("name")
        return self.greeter.greet(name)

    @get("/protected")
    def protected(self, context: RequestContext):
        user = context["user"]
        return f"Access granted to: {user}"

    @get("/logout")
    def logout(self):
        return HttpResponse(
            status=HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": 'Basic realm="localhost:8000"'},
        )
