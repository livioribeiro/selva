from typing import Annotated

from aiomcache import Client
from asgikit.responses import respond_text

from selva.di import Inject
from selva.web import get


@get
async def index(request, memcached: Annotated[Client, Inject]):
    await memcached.set(b"key", b"value")
    result = (await memcached.get(b"key")).decode("utf-8")

    await respond_text(request.response, result)
    await memcached.delete(b"key")
