from redis.asyncio import Redis
from redis.backoff import (
    AbstractBackoff,
    ConstantBackoff,
    DecorrelatedJitterBackoff,
    EqualJitterBackoff,
    ExponentialBackoff,
    FullJitterBackoff,
    NoBackoff,
)
from redis.retry import Retry

from selva.configuration.settings import Settings
from selva.ext.data.redis.settings import RedisSettings

from .settings import BackoffSchema, RetrySchema


def build_backoff(data: BackoffSchema) -> AbstractBackoff:
    if "no_backoff" in data.model_fields_set:
        return NoBackoff()

    if value := data.constant:
        return ConstantBackoff(**value.model_dump(exclude_unset=True))

    if value := data.exponential:
        return ExponentialBackoff(**value.model_dump(exclude_unset=True))

    if value := data.full_jitter:
        return FullJitterBackoff(**value.model_dump(exclude_unset=True))

    if value := data.equal_jitter:
        return EqualJitterBackoff(**value.model_dump(exclude_unset=True))

    if value := data.decorrelated_jitter:
        return DecorrelatedJitterBackoff(**value.model_dump(exclude_unset=True))

    raise ValueError("No value defined for 'backoff'")


def build_retry(data: RetrySchema):
    kwargs = {
        "backoff": build_backoff(data.backoff),
        "retries": data.retries,
    }

    if supported_errors := data.supported_errors:
        kwargs["supported_errors"] = supported_errors

    return Retry(**kwargs)


def make_service(name: str):
    async def redis_service(
        settings: Settings,
    ) -> Redis:
        redis_settings = RedisSettings.model_validate(dict(settings.data.redis[name]))

        kwargs = redis_settings.model_dump(exclude_unset=True)
        if (options := redis_settings.options) and (retry := options.retry):
            kwargs["retry"] = build_retry(retry)

        if url := kwargs.pop("url", ""):
            redis = Redis.from_url(url, **kwargs)
        else:
            redis = Redis(**kwargs)

        await redis.initialize()
        yield redis
        await redis.aclose()

    return redis_service
