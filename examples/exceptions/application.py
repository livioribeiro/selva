from http import HTTPStatus

from selva.web import get
from selva.web.exception import HTTPException, HTTPUnauthorizedException


@get("/unauthorized")
async def not_found(request):
    raise HTTPUnauthorizedException()


@get("/im-a-teapot")
async def im_a_teapot(request):
    raise HTTPException(status=HTTPStatus.IM_A_TEAPOT)
