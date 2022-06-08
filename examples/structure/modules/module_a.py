from selva.web import JsonResponse, RequestContext, controller, get


@controller("/")
class Controller:
    @get
    def index(self) -> JsonResponse:
        return JsonResponse({"location": "index"})

    @get("/hello/{name}")
    async def hello(self, name: str, context: RequestContext) -> JsonResponse:
        return JsonResponse({"hello": name, "request": context.path})
