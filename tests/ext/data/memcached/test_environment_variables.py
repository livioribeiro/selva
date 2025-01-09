import os
from importlib.util import find_spec

import pytest

from selva.configuration.settings import _get_settings_nocache
from selva.ext.data.memcached.service import make_service

MEMCACHED_ADDR = os.getenv("MEMCACHED_ADDR")


pytestmark = [
    pytest.mark.skipif(MEMCACHED_ADDR is None, reason="MEMCACHED_ADDR not defined"),
    pytest.mark.skipif(find_spec("aiomcache") is None, reason="aiomcache not present"),
]


async def test_address_from_environment_variables(monkeypatch):
    monkeypatch.setenv("SELVA__DATA__MEMCACHED__DEFAULT__ADDRESS", MEMCACHED_ADDR)
    settings = _get_settings_nocache()

    addr = MEMCACHED_ADDR.split(":")
    host = addr[0]
    port = int(addr[1]) if len(addr) > 1 else 11211

    async for memcached in make_service("default")(settings):
        assert memcached._pool._host == host
        assert memcached._pool._port == port
