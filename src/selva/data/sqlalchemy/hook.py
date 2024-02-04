from selva.configuration.settings import Settings
from selva.data.sqlalchemy.service import (
    make_engine_service,
    make_sessionmaker_service,
)
from selva.di.container import Container
from selva.di.hook import hook


@hook
def sqlalchemy_hook(container: Container, settings: Settings):
    for name in settings.data.sqlalchemy:
        service_name = name if name != "default" else None

        container.register(make_engine_service(name), name=service_name)
        container.register(make_sessionmaker_service(service_name), name=service_name)
