from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.di.decorator import service as service_decorator, resource as resource_decorator
from selva.ext.data.sqlalchemy.service import (
    make_engine_service,
    make_sessionmaker_service,
)
from selva.ext.data.sqlalchemy.resource import make_session_resource


async def _test_engine_service(settings: Settings):
    engine_service = make_engine_service("default")(settings)
    async for engine in engine_service:
        async with engine.connect() as conn:
            result = await conn.execute(text("select 1"))
            assert result.scalar() == 1

        await engine.dispose()


async def test_make_engine_service_with_url():
    ioc = Container()

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

    ioc.define(Settings, settings)
    ioc.register(service_decorator(make_engine_service("default")))
    ioc.register(service_decorator(make_sessionmaker_service("default")))
    ioc.register(resource_decorator(make_session_resource("default")))

    context = tuple()
    session = await ioc.get(AsyncSession, context=context)

    async with session.begin():
        result = await session.execute(text("select 1"))
        assert result.scalar() == 1

    await ioc._run_finalizers(context=context)
