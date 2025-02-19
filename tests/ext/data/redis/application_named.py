from typing import Annotated

from redis.asyncio import Redis

from selva.di import Inject
from selva.web import get


@get
async def index(request, redis: Annotated[Redis, Inject(name="other")]):
    await redis.set("key", "value")
    result = (await redis.get("key")).decode("utf-8")

    await request.respond(result)
    await redis.delete("key")
