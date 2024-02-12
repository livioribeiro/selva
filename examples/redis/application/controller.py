from typing import Annotated

from asgikit.responses import respond_json
from selva.di import Inject
from selva.web import controller, get

from .service import RedisService


@controller
class Controller:
    redis_service: Annotated[RedisService, Inject]

    @get
    async def index(self, request):
        number = await self.redis_service.get_incr()
        await respond_json(request.response, {"number": number})
