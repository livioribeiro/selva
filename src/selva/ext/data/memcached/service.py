from emcache import Client, MemcachedHostAddress, create_client

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.di.decorator import service as service_decorator, DI_ATTRIBUTE_SERVICE

from .settings import MemcachedSettings


def parse_memcahced_hostaddress(address: str) -> MemcachedHostAddress:
    match address.split(":"):
        case (host,):
            return MemcachedHostAddress(host, 11211)
        case (host, port):
            port = int(port)
            return MemcachedHostAddress(host, port)


def build_memcached_hostaddress(address: str) -> list[MemcachedHostAddress]:
    return [parse_memcahced_hostaddress(addr) for addr in address.split(",")]


def make_service(name: str):
    async def memcached_service(
        settings: Settings,
        di: Container,
    ) -> Client:
        memcached_settings = MemcachedSettings.model_validate(
            dict(settings.data.memcached[name])
        )

        if options := memcached_settings.options:
            memcached_options = options.model_dump(exclude_unset=True)

            if cluster_events := options.cluster_events:
                if not hasattr(cluster_events, DI_ATTRIBUTE_SERVICE):
                    service_decorator(cluster_events, name=name)

                if not di.has(cluster_events, name=name):
                    di.register(cluster_events)

                cluster_events_service_name = getattr(cluster_events, DI_ATTRIBUTE_SERVICE).name

                memcached_options["cluster_events"] = await di.get(cluster_events, name=cluster_events_service_name)

        else:
            memcached_options = {}

        hostaddress = build_memcached_hostaddress(memcached_settings.address)
        client = await create_client(hostaddress, **memcached_options)

        yield client
        await client.close()

    return memcached_service
