from typing import Annotated

from asgikit.responses import respond_text
from aiomcache import Client

from selva.di import Inject
from selva.web import get


@get
async def index(request, memcached: Annotated[Client, Inject(name="other")]):
    await memcached.set(b"key", b"value")
    result = (await memcached.get(b"key")).decode("utf-8")

    await respond_text(request.response, result)
    await memcached.delete(b"key")
