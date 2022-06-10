from selva.web import Application, RequestContext, controller, get


@controller("/")
class Controller:
    @get
    async def index(self, context: RequestContext):
        name = context.query.get("name", "World")
        return f"Hello, {name}!"


app = Application()
app.register(Controller)
