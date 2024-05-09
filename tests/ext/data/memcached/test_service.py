import os
from importlib.util import find_spec

import pytest
from emcache import ClusterEvents, ClusterManagment, MemcachedHostAddress

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.di import Container
from selva.ext.data.memcached.service import make_service

MEMCACHED_ADDR = os.getenv("MEMCACHED_ADDR")

pytestmark = [
    pytest.mark.skipif(MEMCACHED_ADDR is None, reason="MEMCACHED_ADDR not defined"),
    pytest.mark.skipif(find_spec("emcache") is None, reason="emcache not present"),
]


async def _test_engine_service(settings: Settings, ioc: Container):
    service = make_service("default")(settings, ioc)
    async for memcached in service:
        await memcached.set(b"test", b"test")
        result = await memcached.get(b"test")
        assert result.value == b"test"
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

    await _test_engine_service(settings, Container())


async def test_make_service_with_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "memcached": {
                    "default": {
                        "address": MEMCACHED_ADDR,
                        "options": {
                            "timeout": 1.0,
                        },
                    },
                },
            },
        }
    )

    service = make_service("default")(settings, Container())
    async for memcached in service:
        assert memcached._timeout == 1.0


class MyClusterEvents(ClusterEvents):
    async def on_node_healthy(
        self, cluster_managment: ClusterManagment, host: MemcachedHostAddress
    ):
        pass

    async def on_node_unhealthy(
        self, cluster_managment: ClusterManagment, host: MemcachedHostAddress
    ):
        pass


async def test_make_service_with_cluster_events():
    settings = Settings(
        default_settings
        | {
            "data": {
                "memcached": {
                    "default": {
                        "address": MEMCACHED_ADDR,
                        "options": {
                            "cluster_events": f"{__name__}.{MyClusterEvents.__qualname__}"
                        },
                    },
                },
            },
        }
    )

    service = make_service("default")(settings, Container())
    async for memcached in service:
        assert isinstance(memcached._cluster._cluster_events, MyClusterEvents)
