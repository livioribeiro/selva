from typing import Annotated

from aiomcache import Client
from aiomcache.exceptions import ClientException

from selva.di import service, Inject


@service
class MemcachedService:
    memcached: Annotated[Client, Inject]

    async def get_incr(self) -> int:
        try:
            value = await self.memcached.incr(b"number")
        except ClientException:
            await self.memcached.add(b"number", b"0")
            value = await self.memcached.incr(b"number")

        return int(value)
