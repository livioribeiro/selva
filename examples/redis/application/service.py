from typing import Annotated

from redis.asyncio import Redis

from selva.di import service, Inject


@service
class RedisService:
    redis: Annotated[Redis, Inject]

    async def initialize(self):
        await self.redis.set("number", 0, ex=60)

    async def get_incr(self) -> int:
        return await self.redis.incr("number")

