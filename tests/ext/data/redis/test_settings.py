import itertools

import pytest
from redis.backoff import (
    ConstantBackoff,
    DecorrelatedJitterBackoff,
    EqualJitterBackoff,
    ExponentialBackoff,
    FullJitterBackoff,
    NoBackoff,
)

from selva.ext.data.redis.settings import (
    BackoffSchema,
    RedisOptions,
    RedisSettings,
    RetrySchema,
)


@pytest.mark.parametrize(
    "values",
    [
        {"host": "host"},
        {"port": 5432},
        {"db": 0},
        {"host": "host", "port": 5423},
        {"host": "host", "port": 5432, "db": 0},
    ],
    ids=[
        "host",
        "port",
        "db",
        "host_port",
        "host_port_db",
    ],
)
def test_mutually_exclusive_connection_properties(values: dict):
    with pytest.raises(ValueError):
        RedisSettings.model_validate({"url": "url"} | values)


@pytest.mark.parametrize(
    "backoff, cls",
    [
        ({"no_backoff": None}, NoBackoff),
        ({"constant": {"backoff": 1}}, ConstantBackoff),
        ({"exponential": {"cap": 1, "base": 1}}, ExponentialBackoff),
        ({"full_jitter": {"cap": 1, "base": 1}}, FullJitterBackoff),
        ({"equal_jitter": {"cap": 1, "base": 1}}, EqualJitterBackoff),
        ({"decorrelated_jitter": {"cap": 1, "base": 1}}, DecorrelatedJitterBackoff),
    ],
)
def test_retry_backoff(backoff, cls):
    model = RetrySchema.model_validate(
        {
            "backoff": backoff,
            "retries": 1,
        }
    )

    config = model.model_dump(exclude_none=True)
    assert isinstance(config["backoff"], cls)


@pytest.mark.parametrize(
    "values",
    [
        left | right
        for left, right in itertools.combinations(
            [
                {"no_backoff": None},
                {"constant": {"backoff": 1}},
                {"exponential": {"cap": 1, "base": 1}},
                {"full_jitter": {"cap": 1, "base": 1}},
                {"equal_jitter": {"cap": 1, "base": 1}},
                {"decorrelated_jitter": {"cap": 1, "base": 1}},
            ],
            2,
        )
    ],
)
def test_mutually_exclusive_retry_properties(values: dict):
    with pytest.raises(ValueError):
        BackoffSchema.model_validate(values)


def test_invalid_encode_errors_property():
    with pytest.raises(ValueError):
        RedisOptions.model_validate({"encoding_errors": "invalid"})
