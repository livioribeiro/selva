import os
from importlib.util import find_spec
from urllib.parse import urlparse

import pytest

from selva.configuration.settings import _get_settings_nocache
from selva.ext.data.redis.service import make_service

REDIS_URL = os.getenv("REDIS_URL")
PARSED_URL = urlparse(REDIS_URL) if REDIS_URL else None


pytestmark = [
    pytest.mark.skipif(REDIS_URL is None, reason="REDIS_URL not defined"),
    pytest.mark.skipif(find_spec("redis") is None, reason="redis not present"),
]


async def test_url_from_environment_variables(monkeypatch):
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__URL", REDIS_URL)
    settings = _get_settings_nocache()

    async for redis in make_service("default")(settings):
        connection_kwargs = redis.connection_pool.connection_kwargs
        assert connection_kwargs["host"] == PARSED_URL.hostname
        assert connection_kwargs["port"] == PARSED_URL.port
        assert connection_kwargs["db"] == int(PARSED_URL.path.strip("/"))
        assert connection_kwargs.get("username") == PARSED_URL.username
        assert connection_kwargs.get("password") == PARSED_URL.password


async def test_url_username_password_from_environment_variables(monkeypatch):
    url = f"redis://{PARSED_URL.hostname}:{PARSED_URL.port}/{PARSED_URL.path}"
    username = PARSED_URL.username
    password = PARSED_URL.password

    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__URL", url)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__USERNAME", username)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__PASSWORD", password)
    settings = _get_settings_nocache()

    async for redis in make_service("default")(settings):
        connection_kwargs = redis.connection_pool.connection_kwargs
        assert connection_kwargs["host"] == PARSED_URL.hostname
        assert connection_kwargs["port"] == PARSED_URL.port
        assert connection_kwargs["db"] == int(PARSED_URL.path.strip("/"))
        assert connection_kwargs.get("username") == PARSED_URL.username
        assert connection_kwargs.get("password") == PARSED_URL.password


async def test_url_components_from_environment_variables(monkeypatch):
    host = PARSED_URL.hostname
    port = str(PARSED_URL.port)
    database = PARSED_URL.path.strip("/")
    username = PARSED_URL.username
    password = PARSED_URL.password

    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__HOST", host)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__PORT", port)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__DB", database)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__USERNAME", username)
    monkeypatch.setenv("SELVA__DATA__REDIS__DEFAULT__PASSWORD", password)

    settings = _get_settings_nocache()

    async for redis in make_service("default")(settings):
        connection_kwargs = redis.connection_pool.connection_kwargs
        assert connection_kwargs["host"] == PARSED_URL.hostname
        assert connection_kwargs["port"] == PARSED_URL.port
        assert connection_kwargs["db"] == int(PARSED_URL.path.strip("/"))
        assert connection_kwargs.get("username") == PARSED_URL.username
        assert connection_kwargs.get("password") == PARSED_URL.password
