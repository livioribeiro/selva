from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container

from selva.ext.data.sqlalchemy.service import (
    make_engine_service,
    engine_dict_service,
    sessionmaker_service,
)


def init_extension(container: Container, settings: Settings):
    if find_spec("sqlalchemy") is None:
        raise ModuleNotFoundError(
            "Missing 'sqlalchemy'. Install 'selva' with 'sqlalchemy' extra."
        )

    for name in settings.data.sqlalchemy.connections:
        container.register(
            make_engine_service(name if name != "default" else None)
        )

    container.register(engine_dict_service)
    container.register(sessionmaker_service)
