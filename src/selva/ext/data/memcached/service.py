from emcache import Client, MemcachedHostAddress, create_client

from selva.configuration.settings import Settings
from selva.di import Container

from .settings import MemcachedSettings


def parse_memcahced_hostaddress(address: str) -> MemcachedHostAddress:
    match address.split(":"):
        case (host,):
            return MemcachedHostAddress(host, 11211)
        case (host, port):
            port = int(port)
            return MemcachedHostAddress(host, port)


def build_memcached_hostaddress(address: str | list[str]) -> list[MemcachedHostAddress]:
    if isinstance(address, str):
        address = [address]

    return [parse_memcahced_hostaddress(addr) for addr in address]


async def make_service(name: str, container: Container):
    async def memcached_service(
        settings: Settings,
    ) -> Client:
        memcached_settings = MemcachedSettings.model_validate(
            dict(settings.data.memcached[name])
        )

        if options := memcached_settings.options:
            memcached_options = options.model_dump(exclude_unset=True)

            if events := options.cluster_events:
                cluster_events = [
                    await container.create(cluster_event) for cluster_event in events
                ]
                options.cluster_events = cluster_events

        else:
            memcached_options = {}

        hostaddress = build_memcached_hostaddress(memcached_settings.address)
        client = await create_client(hostaddress, **memcached_options)

        yield client
        await client.close()

    return memcached_service
