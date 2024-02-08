from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from selva.configuration.settings import Settings
from selva.di import Inject
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


def make_sessionmaker_service(name: str):
    async def sessionmaker_service(
        engine: Annotated[AsyncEngine, Inject(name=name)],
    ) -> async_sessionmaker:
        return async_sessionmaker(bind=engine)

    return sessionmaker_service
