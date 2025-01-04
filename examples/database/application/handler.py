from http import HTTPStatus
from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_json

from selva.di import Inject
from selva.web import get

from .service import Repository


@get
async def count(request: Request, repository: A[Repository, Inject]):
    current_count = await repository.count()
    await respond_json(request.response, {"count": current_count})


@get("/test")
async def test(request: Request, repository: A[Repository, Inject]):
    response = request.response

    try:
        await repository.test()
        await respond_json(response, {"status": "OK"})
    except Exception as err:
        response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        await respond_json(response, {"status": "FAIL", "message": str(err)})
