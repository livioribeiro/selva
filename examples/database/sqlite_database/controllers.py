from http import HTTPStatus

from asgikit.responses import JsonResponse

from selva.web import controller, get

from .services import Repository


@controller("/")
class Controller:
    def __init__(self, repository: Repository):
        self.repository = repository

    @get
    async def count(self) -> JsonResponse:
        count = await self.repository.count()
        return JsonResponse({"count": count})

    @get("/test")
    async def test(self) -> JsonResponse:
        try:
            await self.repository.test()
            return JsonResponse({"status": "OK"})
        except Exception as e:
            return JsonResponse(
                {"status": "FAIL", "message": str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
