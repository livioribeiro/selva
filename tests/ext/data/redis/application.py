from typing import Annotated

from asgikit.responses import respond_text
from redis.asyncio import Redis

from selva.di import Inject
from selva.web import get


@get
async def index(request, redis: Annotated[Redis, Inject]):
    await redis.set("key", "value")
    result = (await redis.get("key")).decode("utf-8")

    await respond_text(request.response, result)
    await redis.delete("key")
