from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.ext.data.sqlalchemy.middleware import request_scoped_session
from selva.ext.data.sqlalchemy.service import (
    engine_dict_service,
    make_engine_service,
    sessionmaker_service,
    ScopedSession,
)


def init_extension(container: Container, settings: Settings):
    if find_spec("sqlalchemy") is None:
        raise ModuleNotFoundError(
            "Missing 'sqlalchemy'. Install 'selva' with 'sqlalchemy' extra."
        )

    for name in settings.data.sqlalchemy.connections:
        container.register(make_engine_service(name))

    container.register(engine_dict_service)
    container.register(sessionmaker_service)

    if f"{request_scoped_session.__module__}.{request_scoped_session.__name__}" in settings.middleware:
        container.register(ScopedSession)
