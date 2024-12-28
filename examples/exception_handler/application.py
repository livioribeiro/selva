from asgikit.responses import respond_json

from selva.di import service
from selva.web import get
from selva.web.exception_handler import exception_handler


@service
class MyService:
    def parse_exception(self, exc: Exception) -> dict:
        return {"exception": exc.__class__.__name__}


class MyException(Exception):
    pass


@exception_handler(MyException)
async def handle_exception(request, exc, my_service: MyService):
    await respond_json(request.response, my_service.parse_exception(exc))


@get
async def index(request):
    raise MyException()
