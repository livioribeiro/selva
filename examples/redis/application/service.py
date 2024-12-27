from redis.asyncio import Redis

from selva.di import service


@service
async def redis_service(locator) -> "RedisService":
    redis = await locator.get(Redis)
    await redis.set("number", 0, ex=60)
    return RedisService(redis)


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_incr(self) -> int:
        return await self.redis.incr("number")

