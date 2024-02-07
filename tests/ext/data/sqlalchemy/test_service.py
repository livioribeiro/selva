from sqlalchemy import text

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.data.sqlalchemy.service import (
    make_engine_service,
    make_sessionmaker_service,
)


async def _test_engine_service(settings: Settings):
    engine_service = make_engine_service("default")(settings)
    engine = await anext(engine_service)

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
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:",
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
                    "default": {
                        "drivername": "sqlite+aiosqlite",
                        "database": ":memory:",
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
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:",
                        "options": {
                            "echo": True,
                            "echo_pool": True,
                        },
                    },
                },
            },
        }
    )

    engine_service = make_engine_service("default")(settings)
    engine = await anext(engine_service)
    assert engine.echo is True
    assert engine.pool.echo is True


async def test_make_engine_service_with_execution_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
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
        }
    )

    engine_service = make_engine_service("default")
    engine = await anext(engine_service(settings))
    sessionmaker_service = make_sessionmaker_service("default")
    sessionmaker = await sessionmaker_service(engine)

    async with sessionmaker() as session:
        result = await session.execute(text("select 1"))
        assert result.context.execution_options["isolation_level"] == "READ UNCOMMITTED"