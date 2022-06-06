from http import HTTPStatus

import asyncpg
from asgikit.responses import JsonResponse

from selva.web import controller, get


@controller("/postgres")
class Controller:
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    @get
    async def index(self) -> JsonResponse:
        try:
            await self.connection.execute("select 1")
            return JsonResponse({"status": "OK"})
        except Exception as e:
            return JsonResponse(
                {"status": "FAIL", "message": str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
