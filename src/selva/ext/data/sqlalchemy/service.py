from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from selva.configuration.settings import Settings
from selva.di import Container, Inject
from selva.ext.data.sqlalchemy.settings import SqlAlchemyEngineSettings

from .settings import SqlAlchemySettings


def make_engine_service(name: str):
    async def engine_service(
        settings: Settings,
    ) -> AsyncEngine:
        sa_settings = SqlAlchemyEngineSettings.model_validate(
            settings.data.sqlalchemy.connections[name]
        )
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
        for db in settings.data.sqlalchemy.connections
    }


async def sessionmaker_service(
    engines: dict[str, AsyncEngine],
    settings: Settings,
) -> async_sessionmaker:
    sqlalchemy_settings = SqlAlchemySettings.model_validate(settings.data.sqlalchemy)
    if session_options := sqlalchemy_settings.session.options:
        options = session_options.model_dump(exclude_unset=True)
    else:
        options = {}

    if binds := sqlalchemy_settings.session.binds:
        binds_config = {}
        for mapper, engine_name in binds.items():
            if engine := engines.get(engine_name):
                binds_config[mapper] = engine
            else:
                raise ValueError(f"No engine with name '{engine_name}'")

        return async_sessionmaker(binds=binds_config, **options)
    else:
        engine = engines.get("default")
        if not engine:
            name, engine = next(iter(engines.items()))
            logger.warning("Using connection '{}' for sqlalchemy session", name)

        return async_sessionmaker(engine, **options)
