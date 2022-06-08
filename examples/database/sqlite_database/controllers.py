from http import HTTPStatus

from selva.web import JsonResponse, controller, get

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
        except Exception as err:
            return JsonResponse(
                {"status": "FAIL", "message": str(err)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
