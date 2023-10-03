from http import HTTPStatus
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import Response, respond_json

from selva.di import Inject
from selva.web import controller, get

from .service import Repository


@controller
class Controller:
    repository: Annotated[Repository, Inject]

    @get
    async def count(self, request: Request, response: Response):
        count = await self.repository.count()
        await respond_json(response, {"count": count})

    @get("/test")
    async def test(self, request: Request, response: Response):
        try:
            await self.repository.test()
            await respond_json(response, {"status": "OK"})
        except Exception as err:
            await respond_json(
                response,
                {"status": "FAIL", "message": str(err)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
