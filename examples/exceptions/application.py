from http import HTTPStatus

from selva.web import controller, get
from selva.web.exception import HTTPException, HTTPUnauthorizedException


@controller
class Controller:
    @get("/unauthorized")
    async def not_found(self, request, response):
        raise HTTPUnauthorizedException()

    @get("/im-a-teapot")
    async def im_a_teapot(self, request, response):
        raise HTTPException(status=HTTPStatus.IM_A_TEAPOT)
