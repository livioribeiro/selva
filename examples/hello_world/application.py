from typing import Annotated

from asgikit.requests import Request, read_json
from asgikit.responses import Response, respond_json

from selva.di import Inject, service
from selva.web import controller, get, post, FromQuery

from pydantic import BaseModel


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
        response: Response,
        name: Annotated[str, FromQuery("name")] = "World",
        number: Annotated[int, FromQuery] = 1
    ):
        greeting = self.greeter.greet(name)
        await respond_json(response, {"greeting": greeting, "number": number})

    @get("/:name")
    async def greet_path(self, request: Request, response: Response, name: str):
        greeting = self.greeter.greet(name)
        await respond_json(response, {"greeting": greeting})

    @post
    async def post_data(self, request: Request, response: Response):
        body = await read_json(request)
        await respond_json(response, {"result": body})

    @post("pydantic")
    async def post_data_pydantic(self, request: Request, response: Response, data: MyModel):
        await respond_json(response, {"name": data.name, "region": data.region})

    @post("pydantic/list")
    async def post_data_pydantic_list(self, request: Request, response: Response, data: list[MyModel]):
        await respond_json(response, {"data": [d.model_dump() for d in data]})
