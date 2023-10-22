from http import HTTPStatus
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_json, respond_status

from selva.di import Inject
from selva.web import controller, get

from .auth import User
from .service import Greeter


@controller
class Controller:
    greeter: Annotated[Greeter, Inject]

    @get
    async def index(self, request: Request):
        name = request.query.get("name")
        await respond_json(request.response, {"message": self.greeter.greet(name)})

    @get("/protected")
    async def protected(self, request: Request, user: User):
        await respond_json(
            request.response, {"message": f"Access granted to: {user.name}"}
        )

    @get("/logout")
    async def logout(self, request: Request):
        response = request.response
        response.header("WWW-Authenticate", 'Basic realm="localhost:8000"')
        await respond_status(response, HTTPStatus.UNAUTHORIZED)
