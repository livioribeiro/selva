from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container

from .service import make_service


def init_extension(container: Container, settings: Settings):
    if find_spec("redis") is None:
        raise ModuleNotFoundError(
            "Missing 'redis'. Install 'selva' with 'redis' extra."
        )

    for name in settings.data.redis:
        container.register(make_service(name))
