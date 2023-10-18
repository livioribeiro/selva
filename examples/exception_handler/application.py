from asgikit.responses import respond_json

from selva.web import controller, get
from selva.web.exception_handler import exception_handler


class MyException(Exception):
    pass


@exception_handler(MyException)
class MyExceptionHandler:
    async def handle_exception(self, request, response, exc):
        await respond_json(response, {"exception": exc.__class__.__name__})


@controller
class Controller:
    @get
    async def index(self, request, response):
        raise MyException()
