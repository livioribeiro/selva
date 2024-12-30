from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.ext.data.sqlalchemy.service import (
    engine_dict_service,
    make_engine_service,
    sessionmaker_service,
)


async def _test_engine_service(settings: Settings):
    engine_service = make_engine_service("default")(settings)
    async for engine in engine_service:
        async with engine.connect() as conn:
            result = await conn.execute(text("select 1"))
            assert result.scalar() == 1

        await engine.dispose()


async def test_make_engine_service_with_url():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
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
                            "drivername": "sqlite+aiosqlite",
                            "database": ":memory:",
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
                            "url": "sqlite+aiosqlite:///:memory:",
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
                            "url": "sqlite+aiosqlite:///:memory:",
                            "options": {
                                "execution_options": {
                                    "isolation_level": "READ UNCOMMITTED"
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
            assert isolation_level == "READ UNCOMMITTED"

        await engine.dispose()


async def test_make_engine_service_alternative_name():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "other": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                },
            },
        }
    )

    engine_service = make_engine_service("other")(settings)
    async for engine in engine_service:
        assert engine is not None
        await engine.dispose()


async def test_sessionmaker_service():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.data.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        result = await session.execute(text("select 1"))
        assert result.scalar() == 1

    await engine.dispose()


async def test_engine_dict_service():
    ioc = Container()

    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                        "other": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                },
            },
        }
    )

    ioc.define(Settings, settings)
    ioc.define(
        AsyncEngine,
        create_async_engine(settings.data.sqlalchemy.connections.default.url),
    )
    ioc.define(
        AsyncEngine,
        create_async_engine(settings.data.sqlalchemy.connections.other.url),
        name="other",
    )

    engines = await engine_dict_service(settings, ioc)

    assert set(engines.keys()) == {"default", "other"}
