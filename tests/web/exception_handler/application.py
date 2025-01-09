from asgikit.responses import respond_json, respond_text

from selva.web.exception_handler.decorator import exception_handler
from selva.web.routing.decorator import get


class MyException(Exception):
    pass


class MyBaseException(Exception):
    pass


class DerivedException(MyBaseException):
    pass


@exception_handler(MyException)
async def my_exception_handler(exc, request):
    await respond_json(request.response, {"exception": exc.__class__.__name__})


@exception_handler(BaseException)
async def base_exception_handler(exc, request):
    await respond_text(
        request.response, f"handler=base; exception={exc.__class__.__name__}"
    )


@get
async def index(request):
    raise MyException()


@get("base")
async def base(request):
    raise MyBaseException()


@get("derived")
async def derived(request):
    raise DerivedException()
