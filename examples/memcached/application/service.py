from typing import Annotated

from aiomcache import Client as Memcached

from selva.di import Inject, service


@service
class MemcachedService:
    memcached: Annotated[Memcached, Inject]

    async def initialize(self):
        if not await self.memcached.get(b"number"):
            await self.memcached.add(b"number", b"0")

    async def get_incr(self) -> int:
        value = await self.memcached.incr(b"number")
        return int(value)
