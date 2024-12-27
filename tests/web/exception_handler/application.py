from asgikit.responses import respond_json

from selva.di import service
from selva.web import get, ExceptionHandler


class MyException(Exception):
    pass


# class MyExceptionHandler:
#     async def __call__(self, request, exc):
#         await respond_json(request.response, {"exception": exc.__class__.__name__})


@service
def my_exception_handler() -> ExceptionHandler[MyException]:
    async def _handler(request, exc):
        await respond_json(request.response, {"exception": exc.__class__.__name__})

    return _handler



@get
async def index(request):
    raise MyException()
