from typing import Annotated

from asgikit.responses import respond_text
from emcache import Client

from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    memcached: Annotated[Client, Inject(name="other")]

    @get
    async def index(self, request):
        await self.memcached.set(b"key", b"value")
        result = (await self.memcached.get(b"key")).value.decode("utf-8")

        await respond_text(request.response, result)
        await self.memcached.delete(b"key")
