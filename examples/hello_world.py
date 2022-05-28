from asgikit.requests import HttpRequest
from asgikit.responses import PlainTextResponse

from selva.web.application import Application
from selva.web.routing.decorators import controller, get


@controller(path="/")
class Controller:
    @get
    def index(self, req: HttpRequest) -> PlainTextResponse:
        name = req.query.get_first("name", "World")
        return PlainTextResponse(f"Hello, {name}!")


app = Application()
app.controllers(Controller)
