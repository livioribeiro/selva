from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container

from .service import make_service


def selva_extension(container: Container, settings: Settings):
    if find_spec("redis") is None:
        return

    for name in settings.data.redis:
        service_name = name if name != "default" else None

        container.register(make_service(name), name=service_name)
