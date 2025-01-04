from typing import Annotated as A

from redis.asyncio import Redis

from selva.di import service, Inject


@service
class RedisService:
    redis: A[Redis, Inject]

    async def get_incr(self) -> int:
        return await self.redis.incr("number")
