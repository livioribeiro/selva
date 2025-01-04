import os
from importlib.util import find_spec

import pytest
from sqlalchemy import make_url

from selva.configuration.settings import _get_settings_nocache
from selva.ext.data.sqlalchemy.service import make_engine_service

POSTGRES_URL = os.getenv("POSTGRES_URL")
SA_DB_URL = make_url(POSTGRES_URL) if POSTGRES_URL else None


async def test_database_url_from_environment_variables(monkeypatch):
    url = "sqlite+aiosqlite:///:memory:"
    monkeypatch.setenv("SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__URL", url)
    settings = _get_settings_nocache()

    async for engine in make_engine_service("default")(settings):
        assert str(engine.url) == url


@pytest.mark.skipif(SA_DB_URL is None, reason="POSTGRES_URL not defined")
@pytest.mark.skipif(find_spec("psycopg") is None, reason="psycopg not present")
async def test_database_url_username_password_from_environment_variables(monkeypatch):
    url = f"postgresql+psycopg://{SA_DB_URL.host}:{SA_DB_URL.port}/{SA_DB_URL.database}"
    username = SA_DB_URL.username
    password = SA_DB_URL.password

    monkeypatch.setenv("SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__URL", url)
    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__USERNAME", username
    )
    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__PASSWORD", password
    )
    settings = _get_settings_nocache()

    async for engine in make_engine_service("default")(settings):
        assert engine.url == SA_DB_URL


@pytest.mark.skipif(SA_DB_URL is None, reason="POSTGRES_URL not defined")
@pytest.mark.skipif(find_spec("psycopg") is None, reason="psycopg not present")
async def test_database_url_components_from_environment_variables(monkeypatch):
    drivername = "postgresql+psycopg"
    host = SA_DB_URL.host
    port = str(SA_DB_URL.port)
    database = SA_DB_URL.database
    username = SA_DB_URL.username
    password = SA_DB_URL.password

    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__DRIVERNAME", drivername
    )
    monkeypatch.setenv("SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__HOST", host)
    monkeypatch.setenv("SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__PORT", port)
    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__DATABASE", database
    )
    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__USERNAME", username
    )
    monkeypatch.setenv(
        "SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__PASSWORD", password
    )
    settings = _get_settings_nocache()

    async for engine in make_engine_service("default")(settings):
        assert engine.url == SA_DB_URL
