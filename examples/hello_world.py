from selva.web import Application, RequestContext, controller, get, post


@controller
class Controller:
    @get
    async def index(self, context: RequestContext):
        name = context.query.get("name", "World")
        return f"Hello, {name}!"

    @get("{name}")
    async def index(self, name: str):
        return {"greeting": f"Hello, {name}!"}

    @post
    async def post(self, context: RequestContext):
        body = await context.json()
        return {"result": body}


app = Application(Controller)
