from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container

from .service import make_service


async def init_extension(container: Container, settings: Settings):
    if find_spec("aiomcache") is None:
        raise ModuleNotFoundError(
            "Missing 'aiomcache'. Install 'selva' with 'memcached' extra."
        )

    for name in settings.data.memcached:
        service_factory = make_service(name)
        container.register(service_factory)
