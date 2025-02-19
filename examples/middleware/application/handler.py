from http import HTTPStatus
from typing import Annotated as A

from selva.di import Inject
from selva.web import get
from selva.web.http import Request, Response

from .auth import User
from .service import Greeter


@get
async def index(request: Request, greeter: A[Greeter, Inject]):
    name = request.query_params.get("name")
    await request.respond({"message": greeter.greet(name)})


@get("/protected")
async def protected(request: Request, user: User):
    await request.respond({"message": f"Access granted to: {user.name}"})


@get("/logout")
async def logout(request: Request):
    response = Response(
        status_code=HTTPStatus.UNAUTHORIZED,
        headers={"WWW-Authenticate": 'Basic realm="localhost:8000"'},
    )
    await request.respond(response)
