from typing import Annotated

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from selva.di import Inject
from selva.web import get


@get
async def index(request, engine: Annotated[AsyncEngine, Inject(name="other")]):
    async with engine.begin() as conn:
        result = await conn.execute(text("select sqlite_version()"))
        version = result.first()[0]

    await request.respond(version)
