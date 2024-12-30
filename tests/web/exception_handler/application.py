from asgikit.responses import respond_json

from selva.web.routing.decorator import get
from selva.web.exception_handler import exception_handler


class MyException(Exception):
    pass


@exception_handler(MyException)
async def my_exception_handler(exc, request):
    await respond_json(request.response, {"exception": exc.__class__.__name__})


@get
async def index(request):
    raise MyException()
