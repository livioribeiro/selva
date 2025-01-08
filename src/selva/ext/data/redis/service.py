from redis.asyncio import Redis

from selva.configuration.settings import Settings
from selva.di.decorator import service

from .settings import RedisSettings


def make_service(name: str):
    @service(name=name if name != "default" else None)
    async def redis_service(settings: Settings) -> Redis:
        redis_settings = RedisSettings.model_validate(dict(settings.data.redis[name]))

        kwargs = redis_settings.model_dump(exclude_unset=True)

        if url := kwargs.pop("url", ""):
            redis = Redis.from_url(url, **kwargs)
        else:
            redis = Redis(**kwargs)

        await redis.initialize()
        yield redis
        await redis.aclose()

    return redis_service
