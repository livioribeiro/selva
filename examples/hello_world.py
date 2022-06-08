from selva.web import Application, PlainTextResponse, RequestContext, controller, get


@controller("/")
class Controller:
    @get
    async def index(self, context: RequestContext) -> PlainTextResponse:
        name = context.query.get("name", "World")
        return PlainTextResponse(f"Hello, {name}!")


app = Application()
app.register(Controller)
