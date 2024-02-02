from typing import Annotated

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from selva.configuration.settings import Settings
from selva.di import service, hook, Inject
from selva.di.container import Container


@hook
async def sqlalchemy_hook(container: Container):
    settings = await container.get(Settings)
    for name in settings.data.sqlalchemy:
        engine_service = make_engine_service(name)

        if name == "default":
            sessionmaker_service = default_sessionmaker_service
            container.register(engine_service)
            container.register(sessionmaker_service)
        else:
            sessionmaker_service = make_sessionmaker_service(name)
            container.register(engine_service, name=name)
            container.register(sessionmaker_service, name=name)


def make_engine_service(name: str):
    async def engine_service(settings: Settings) -> AsyncEngine:
        url = URL.create(**settings.data.sqlalchemy[name])
        engine = create_async_engine(url)
        yield engine
        await engine.dispose()

    return engine_service


def default_sessionmaker_service(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine)


def make_sessionmaker_service(name: str):
    async def sessionmaker_service(engine: AsyncEngine = Inject(name=name)) -> async_sessionmaker:
        return async_sessionmaker(bind=engine)

    return sessionmaker_service
