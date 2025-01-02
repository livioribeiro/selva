import os
from importlib.util import find_spec

import pytest
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import create_async_engine

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.data.sqlalchemy.service import make_engine_service, sessionmaker_service

from .test_service import _test_engine_service

POSTGRES_URL = os.getenv("POSTGRES_URL")

pytestmark = [
    pytest.mark.skipif(POSTGRES_URL is None, reason="POSTGRES_URL not defined"),
    pytest.mark.skipif(find_spec("psycopg") is None, reason="psycopg not present"),
]

SA_DB_URL = make_url(POSTGRES_URL) if POSTGRES_URL else None


async def test_make_engine_service_with_url():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": POSTGRES_URL,
                        },
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_url_username_password():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": f"postgresql+psycopg://{SA_DB_URL.host}:{SA_DB_URL.port}/{SA_DB_URL.database}",
                            "username": SA_DB_URL.username,
                            "password": SA_DB_URL.password,
                        },
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_url_components():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "drivername": "postgresql+psycopg",
                            "host": SA_DB_URL.host,
                            "port": SA_DB_URL.port,
                            "database": SA_DB_URL.database,
                            "username": SA_DB_URL.username,
                            "password": SA_DB_URL.password,
                        },
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": POSTGRES_URL,
                            "options": {
                                "echo": True,
                                "echo_pool": True,
                            },
                        },
                    },
                },
            },
        }
    )

    engine_service = make_engine_service("default")(settings)
    async for engine in engine_service:
        assert engine.echo is True
        assert engine.pool.echo is True


async def test_make_engine_service_with_execution_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": POSTGRES_URL,
                            "options": {
                                "execution_options": {
                                    "isolation_level": "READ COMMITTED"
                                },
                            },
                        },
                    },
                },
            },
        }
    )

    async for engine in make_engine_service("default")(settings):
        async with engine.connect() as conn:
            result = await conn.execute(text("select 1"))
            isolation_level = result.context.execution_options["isolation_level"]
            assert isolation_level == "READ COMMITTED"


async def test_sessionmaker_service():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": POSTGRES_URL,
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(POSTGRES_URL)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        result = await session.execute(text("select 1"))
        assert result.scalar() == 1

    await engine.dispose()
