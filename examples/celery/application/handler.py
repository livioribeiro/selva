import asyncio
from typing import Annotated as A

from selva.web import FromQuery, get

from .celery_tasks import hello


@get("")
async def index(request, name: A[str, FromQuery] = "World"):
    await asyncio.to_thread(hello.delay, name)
    await request.respond("Hello, world!")
