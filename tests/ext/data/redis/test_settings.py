import itertools

import pytest

from selva.ext.data.redis.settings import BackoffSchema, RedisSettings


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
def test_redis_settings_mutually_exclusive_connection_properties(values: dict):
    with pytest.raises(ValueError):
        RedisSettings.model_validate({"url": "url"} | values)


# INPUTS = [
#      {"no_backoff": None},
#      {"constant": {"backoff": 1}},
#      {"exponential": {"cap": 1, "base": 1}},
#      {"full_jitter": {"cap": 1, "base": 1}},
#      {"equal_jitter": {"cap": 1, "base": 1}},
#      {"decorrelated_jitter": {"cap": 1, "base": 1}},
# ]


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
def test_redis_settings_mutually_exclusive_retry_properties(values: dict):
    with pytest.raises(ValueError):
        BackoffSchema.model_validate(values)
