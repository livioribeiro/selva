from typing import Annotated as A

from selva.di import Inject
from selva.web import Request, get

from .service import RedisService


@get
async def index(request: Request, redis_service: A[RedisService, Inject]):
    number = await redis_service.get_incr()
    await request.respond({"number": number})
