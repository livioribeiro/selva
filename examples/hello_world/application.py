from typing import Annotated

from selva.di import Inject, service
from selva.web import RequestContext, controller, get, post, FromQuery

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
    greeter: Greeter = Inject()

    @get
    async def greet_query(
        self,
        name: Annotated[str, FromQuery("name")] = "World",
        number: Annotated[int, FromQuery()] = 1
    ):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting, "number": number}

    @get("/:name")
    async def greet_path(self, name: str):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}

    @post
    async def post_data(self, context: RequestContext):
        body = await context.request.json()
        return {"result": body}

    @post("pydantic")
    def post_data_pydantic(self, data: MyModel) -> dict:
        return {"name": data.name, "region": data.region}

    @post("pydantic/list")
    def post_data_pydantic_list(self, data: list[MyModel]) -> dict:
        return {"data": [d.model_dump() for d in data]}
