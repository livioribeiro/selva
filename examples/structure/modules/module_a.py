from selva.web import RequestContext, controller, get


@controller("/")
class Controller:
    @get
    def index(self):
        return {"location": "index"}

    @get("/hello/{name}")
    async def hello(self, name: str, context: RequestContext):
        return {"hello": name, "request": context.path}
