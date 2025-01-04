import structlog
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.di.decorator import service
from selva.ext.data.sqlalchemy.settings import (
    SqlAlchemyEngineSettings,
    SqlAlchemySettings,
)

logger = structlog.get_logger()


def make_engine_service(name: str):
    @service(name=name if name != "default" else None)
    async def engine_service(settings: Settings) -> AsyncEngine:
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


@service
async def engine_dict_service(
    settings: Settings, di: Container
) -> dict[str, AsyncEngine]:
    return {
        db: await di.get(AsyncEngine, name=db if db != "default" else None)
        for db in settings.data.sqlalchemy.connections
    }


@service
async def sessionmaker_service(
    settings: Settings, engines_map: dict[str, AsyncEngine]
) -> async_sessionmaker:
    sqlalchemy_settings = SqlAlchemySettings.model_validate(settings.data.sqlalchemy)

    args = []

    if session_options := sqlalchemy_settings.session.options:
        kwargs = session_options.model_dump(exclude_unset=True)
    else:
        kwargs = {}

    if binds := sqlalchemy_settings.session.binds:
        binds_config = {}
        for mapper, engine_name in binds.items():
            if engine := engines_map.get(engine_name):
                binds_config[mapper] = engine
            else:
                raise ValueError(f"No engine with name '{engine_name}'")

        kwargs["binds"] = binds_config
    else:
        engine = engines_map.get("default")
        if not engine:
            name, engine = next(iter(engines_map.items()))
            logger.warning("connection for sqlalchemy session", connection=name)
        args.append(engine)

    return async_sessionmaker(*args, **kwargs)
