from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container

from .service import make_service


async def selva_extension(container: Container, settings: Settings):
    if find_spec("emcache") is None:
        raise ModuleNotFoundError("Missing 'emcache'. Install 'selva' with 'memcached' extra.")

    for name in settings.data.memcached:
        service_name = name if name != "default" else None
        service = make_service(name)

        container.register(service, name=service_name)
