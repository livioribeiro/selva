from typing import Annotated

from asgikit.responses import respond_text
from redis.asyncio import Redis

from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    redis: Annotated[Redis, Inject(name="other")]

    @get
    async def index(self, request):
        await self.redis.set("key", "value")
        result = (await self.redis.get("key")).decode("utf-8")

        await respond_text(request.response, result)
        await self.redis.delete("key")
