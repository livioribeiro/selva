import os
from importlib.util import find_spec

import pytest

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.ext.data.memcached.service import make_service, parse_memcached_address

MEMCACHED_ADDR = os.getenv("MEMCACHED_ADDR")

pytestmark = [
    pytest.mark.skipif(MEMCACHED_ADDR is None, reason="MEMCACHED_ADDR not defined"),
    pytest.mark.skipif(find_spec("aiomcache") is None, reason="aiomcache not present"),
]


async def _test_make_service(settings: Settings):
    service = make_service("default")(settings)
    async for memcached in service:
        await memcached.set(b"test", b"test")
        result = await memcached.get(b"test")
        assert result == b"test"
        await memcached.delete(b"test")


async def test_make_service_with_address():
    settings = Settings(
        default_settings
        | {
            "data": {
                "memcached": {
                    "default": {
                        "address": MEMCACHED_ADDR,
                    },
                },
            },
        }
    )

    await _test_make_service(settings)


async def test_make_service_with_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "memcached": {
                    "default": {
                        "address": MEMCACHED_ADDR,
                        "options": {
                            "pool_size": 10,
                            "pool_minsize": 1,
                        },
                    },
                },
            },
        }
    )

    service = make_service("default")(settings)
    async for memcached in service:
        assert memcached._pool._maxsize == 10
        assert memcached._pool._minsize == 1


def test_parse_memcached_address_with_port():
    host, port = parse_memcached_address("memcached:11212")
    assert host == "memcached"
    assert port == 11212


def test_parse_memcached_address_without_port():
    host, port = parse_memcached_address("memcached")
    assert host == "memcached"
    assert port == 11211
