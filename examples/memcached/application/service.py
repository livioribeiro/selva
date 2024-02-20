from typing import Annotated

from emcache import (
    Client,
    ClusterEvents,
    ClusterManagment,
    MemcachedHostAddress,
    NotFoundCommandError,
)

from selva.di import Inject, service


class MyClusterEvents(ClusterEvents):
    async def on_node_healthy(
        self, cluster_managment: ClusterManagment, host: MemcachedHostAddress
    ):
        print(f"Healthy: {host.address}:{host.port}")

    async def on_node_unhealthy(
        self, cluster_managment: ClusterManagment, host: MemcachedHostAddress
    ):
        print(f"Unhealthy: {host.address}:{host.port}")


@service
class MemcachedService:
    memcached: Annotated[Client, Inject]

    async def get_incr(self) -> int:
        try:
            value = await self.memcached.increment(b"number", 1)
        except NotFoundCommandError:
            await self.memcached.add(b"number", b"0")
            value = await self.memcached.increment(b"number", 1)

        return int(value)
