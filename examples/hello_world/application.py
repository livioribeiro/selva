from typing import Annotated as A

from asgikit.requests import Request, read_json
from asgikit.responses import respond_json
from pydantic import BaseModel

import structlog

from selva.di import Inject, service
from selva.web import FromPath, FromQuery, get, post

logger = structlog.get_logger()


class MyModel(BaseModel):
    name: str
    region: str = None


class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@service
def service_greeter() -> Greeter:
    return Greeter()


@get
async def greet_query(
    request: Request,
    greeter: A[Greeter, Inject],
    name: A[str, FromQuery("name")] = "World",
    number: A[int, FromQuery] = 1,
):
    greeting = greeter.greet(name)
    logger.info(greeting, name=name, number=number)
    await respond_json(request.response, {"greeting": greeting, "number": number})


@get("/:name")
async def greet_path(
    request: Request,
    greeter: A[Greeter, Inject],
    name: A[str, FromPath],
):
    greeting = greeter.greet(name)
    await respond_json(request.response, {"greeting": greeting})

@post
async def post_data(request: Request):
    body = await read_json(request)
    await respond_json(request.response, {"result": body})

@post("pydantic")
async def post_data_pydantic(request: Request, data: MyModel):
    await respond_json(request.response, {"name": data.name, "region": data.region})

@post("pydantic/list")
async def post_data_pydantic_list(request: Request, data: list[MyModel]):
    await respond_json(request.response, {"data": [d.model_dump() for d in data]})
