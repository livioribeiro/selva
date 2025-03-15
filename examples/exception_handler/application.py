from typing import Annotated as A

from selva.di import Inject, service
from selva.web import exception_handler, get


@service
class MyService:
    def parse_exception(self, exc: Exception) -> dict:
        return {"exception": exc.__class__.__name__}


class MyException(Exception):
    pass


@exception_handler(MyException)
async def handle_exception(err, request, my_service: A[MyService, Inject]):
    await request.respond(my_service.parse_exception(err))


@get
async def index(request):
    raise MyException()
