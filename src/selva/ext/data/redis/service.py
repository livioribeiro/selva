import socket

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
from selva.di.decorator import service

from .settings import BackoffSchema, RedisSettings, RetrySchema


_socket_keepalive_options_map = {
    "TCP_KEEPIDLE": socket.TCP_KEEPIDLE,
    "TCP_KEEPCNT": socket.TCP_KEEPCNT,
    "TCP_KEEPINTVL": socket.TCP_KEEPINTVL,
}


def build_socket_keepalive_options(data: dict[str, int]) -> dict[int, int]:
    return {_socket_keepalive_options_map[key]: value for key, value in data.items()}


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
    @service(name=name if name != "default" else None)
    async def redis_service(settings: Settings) -> Redis:
        redis_settings = RedisSettings.model_validate(dict(settings.data.redis[name]))

        kwargs = redis_settings.model_dump(exclude_unset=True)
        if options := redis_settings.options:
            if retry := options.retry:
                kwargs["retry"] = build_retry(retry)

            if keepalive_opts := options.socket_keepalive_options:
                kwargs["socket_keepalive_options"] = build_socket_keepalive_options(
                    keepalive_opts
                )

        if url := kwargs.pop("url", ""):
            redis = Redis.from_url(url, **kwargs)
        else:
            redis = Redis(**kwargs)

        await redis.initialize()
        yield redis
        await redis.aclose()

    return redis_service
