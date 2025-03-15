from http import HTTPStatus
from typing import Annotated as A

from selva.di import Inject
from selva.web import Request, get

from .service import Repository


@get
async def count(request: Request, repository: A[Repository, Inject]):
    current_count = await repository.count()
    await request.respond({"count": current_count})


@get("/test")
async def test(request: Request, repository: A[Repository, Inject]):
    try:
        await repository.test()
        await request.respond({"status": "OK"})
    except Exception as err:
        await request.respond(
            {"status": "FAIL", "message": str(err)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
