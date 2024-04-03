from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from selva.configuration.settings import Settings
from selva.di import Container, Inject
from selva.ext.data.sqlalchemy.settings import SqlAlchemySettings


def make_engine_service(name: str):
    async def engine_service(
        settings: Settings,
    ) -> AsyncEngine:
        sa_settings = SqlAlchemySettings.model_validate(settings.data.sqlalchemy[name])
        url = sa_settings.get_url()

        if sa_options := sa_settings.options:
            options = sa_options.model_dump(exclude_unset=True)
        else:
            options = {}

        engine = create_async_engine(url, **options)
        yield engine
        await engine.dispose()

    return engine_service


async def engine_dict_service(
    di: Container, settings: Settings
) -> dict[str, AsyncEngine]:
    return {
        db: await di.get(AsyncEngine, name=db if db != "default" else None)
        for db in settings.data.sqlalchemy
    }


async def sessionmaker_service(engines: dict[str, AsyncEngine]) -> async_sessionmaker:
    default = engines.pop("default", None)

    return async_sessionmaker(bind=default, binds=engines, expire_on_commit=False)
