from http import HTTPStatus
from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_json, respond_status

from selva.di import Inject
from selva.web import get

from .auth import User
from .service import Greeter


@get
async def index(request: Request, greeter: A[Greeter, Inject]):
    name = request.query.get("name")
    await respond_json(request.response, {"message": greeter.greet(name)})


@get("/protected")
async def protected(request: Request, user: User):
    await respond_json(request.response, {"message": f"Access granted to: {user.name}"})


@get("/logout")
async def logout(request: Request):
    response = request.response
    response.header("WWW-Authenticate", 'Basic realm="localhost:8000"')
    await respond_status(response, HTTPStatus.UNAUTHORIZED)
