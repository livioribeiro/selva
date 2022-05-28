from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse

from selva.web.application import Application
from selva.web.routing.decorators import controller, get


@controller(path="/")
class Controller:
    def __init__(self, request: HttpRequest):
        self.request = request

    @get(path="/")
    def index(self) -> JsonResponse:
        return JsonResponse({"location": "index"})

    @get
    async def hello(self, name: str) -> JsonResponse:
        return JsonResponse({"hello": name, "request": self.request.path})


app = Application()
app.controllers(Controller)

