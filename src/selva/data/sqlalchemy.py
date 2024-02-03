from typing import Annotated

from sqlalchemy import URL, make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from selva.configuration.settings import Settings
from selva.di import Inject
from selva.di.hook import hook
from selva.di.container import Container


@hook
def sqlalchemy_hook(container: Container, settings: Settings):
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
        if url := settings.data.sqlalchemy[name].get("url"):
            url = make_url(url)
            if username := settings.data.sqlalchemy[name].get("username"):
                url = url.set(username=username)
            if password := settings.data.sqlalchemy[name].get("password"):
                url = url.set(password=password)
        else:
            connection_params = {
                k: v for k, v in settings.data.sqlalchemy[name].items()
                if k in ("drivername", "host", "port", "database", "username", "password", "query")
            }
            url = URL.create(**connection_params)

        params = settings.data.sqlalchemy[name].get("params", {})
        engine = create_async_engine(url, **params)
        yield engine
        await engine.dispose()

    return engine_service


def default_sessionmaker_service(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine)


def make_sessionmaker_service(name: str):
    async def sessionmaker_service(
        engine: Annotated[AsyncEngine, Inject(name=name)],
    ) -> async_sessionmaker:
        return async_sessionmaker(bind=engine)

    return sessionmaker_service
