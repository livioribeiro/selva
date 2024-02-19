from typing import Annotated

from asgikit.responses import respond_json
from selva.di import Inject
from selva.web import controller, get

from .service import MemcachedService


@controller
class Controller:
    memcached_service: Annotated[MemcachedService, Inject]

    @get
    async def index(self, request):
        number = await self.memcached_service.get_incr()
        await respond_json(request.response, {"number": number})
