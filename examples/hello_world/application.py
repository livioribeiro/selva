import sys
from typing import Annotated

from asgikit.requests import Request, read_json
from asgikit.responses import respond_json
from pydantic import BaseModel

from selva.di import Inject, service
from selva.web import FromPath, FromQuery, controller, get, post

from loguru import logger


class MyModel(BaseModel):
    name: str
    region: str = None


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller
class Controller:
    greeter: Annotated[Greeter, Inject]

    @get
    async def greet_query(
        self,
        request: Request,
        name: Annotated[str, FromQuery("name")] = "World",
        number: Annotated[int, FromQuery] = 1,
    ):
        logger.bind(key="value").info("message")
        greeting = self.greeter.greet(name)
        await respond_json(request.response, {"greeting": greeting, "number": number})

    @get("/:name")
    async def greet_path(self, request: Request, name: Annotated[str, FromPath]):
        greeting = self.greeter.greet(name)
        await respond_json(request.response, {"greeting": greeting})

    @post
    async def post_data(self, request: Request):
        body = await read_json(request)
        await respond_json(request.response, {"result": body})

    @post("pydantic")
    async def post_data_pydantic(self, request: Request, data: MyModel):
        await respond_json(request.response, {"name": data.name, "region": data.region})

    @post("pydantic/list")
    async def post_data_pydantic_list(self, request: Request, data: list[MyModel]):
        await respond_json(request.response, {"data": [d.model_dump() for d in data]})
