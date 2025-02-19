from typing import Annotated

from aiomcache import Client

from selva.di import Inject
from selva.web import get


@get
async def index(request, memcached: Annotated[Client, Inject(name="other")]):
    await memcached.set(b"key", b"value")
    result = (await memcached.get(b"key")).decode("utf-8")

    await request.respond(result)
    await memcached.delete(b"key")
