from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.di.decorator import service as service_decorator, resource as resource_decorator

from .service import make_engine_service, make_sessionmaker_service
from .resource import make_connection_resource, make_session_resource


def selva_extension(container: Container, settings: Settings):
    if find_spec("sqlalchemy") is None:
        return

    for name in settings.data.sqlalchemy:
        service_name = name if name != "default" else None

        container.register(service_decorator(make_engine_service(name), name=service_name))
        container.register(service_decorator(make_sessionmaker_service(service_name), name=service_name))
        container.register(resource_decorator(make_connection_resource(name), name=service_name))
        container.register(resource_decorator(make_session_resource(name), name=service_name))
