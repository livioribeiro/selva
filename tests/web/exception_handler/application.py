from asgikit.responses import respond_json

from selva.web import controller, get
from selva.web.exception_handler import exception_handler


class MyException(Exception):
    pass


@exception_handler(MyException)
class MyExceptionHandler:
    async def handle_exception(self, request, exc):
        await respond_json(request.response, {"exception": exc.__class__.__name__})


@controller
class Controller:
    @get
    async def index(self, request):
        raise MyException()
