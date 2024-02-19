from typing import Annotated

from emcache import Client, ClusterEvents, MemcachedHostAddress, ClusterManagment

from selva.di import service, Inject


class MyClusterEvents(ClusterEvents):
    def on_node_healthy(self, cluster_managment: ClusterManagment, host: MemcachedHostAddress):
        print(f"Healthy: {host.address}:{host.port}")

    def on_node_unhealthy(self, cluster_managment: ClusterManagment, host: MemcachedHostAddress):
        print(f"Unhealthy: {host.address}:{host.port}")


@service
class MemcachedService:
    memcached: Annotated[Client, Inject]

    async def initialize(self):
        await self.memcached.set(b"number", b"0")

    async def get_incr(self) -> int:
        value = await self.memcached.increment(b"number", 1)
        return int(value)

