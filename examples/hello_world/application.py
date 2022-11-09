from selva.di import Inject, service
from selva.web import RequestContext, controller, get, post


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller
class Controller:
    greeter: Greeter = Inject()

    @get
    async def greet_query(self, context: RequestContext):
        name = context.query.get("name", "World")
        greeting = self.greeter.greet(name)
        return greeting

    @get("/:name")
    async def greet_path(self, name: str):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}

    @post
    async def post(self, context: RequestContext):
        body = await context.json()
        return {"result": body}
