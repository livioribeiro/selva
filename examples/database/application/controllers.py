from http import HTTPStatus

from selva.web import JsonResponse, controller, get

from .services import Repository


@controller
class Controller:
    def __init__(self, repository: Repository):
        self.repository = repository

    @get
    async def count(self):
        count = await self.repository.count()
        return {"count": count}

    @get("/test")
    async def test(self):
        try:
            await self.repository.test()
            return {"status": "OK"}
        except Exception as err:
            return JsonResponse(
                {"status": "FAIL", "message": str(err)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
