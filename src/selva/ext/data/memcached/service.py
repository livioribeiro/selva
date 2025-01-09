from aiomcache import Client, FlagClient

from selva.configuration.settings import Settings
from selva.di.decorator import service

from .settings import MemcachedSettings


def parse_memcached_address(address: str) -> tuple[str, int]:
    match address.split(":", maxsplit=1):
        case [host]:
            return host, 11211
        case [host, port]:
            port = int(port)
            return host, port


def make_service(name: str):
    @service(name=name if name != "default" else None)
    async def memcached_service(settings: Settings) -> Client:
        memcached_settings = MemcachedSettings.model_validate(
            dict(settings.data.memcached[name])
        )

        if options := memcached_settings.options:
            memcached_options = options.model_dump(exclude_unset=True)
        else:
            memcached_options = {}

        host, port = parse_memcached_address(memcached_settings.address)
        client = FlagClient(host, port, **memcached_options)

        yield client
        await client.close()

    return memcached_service
