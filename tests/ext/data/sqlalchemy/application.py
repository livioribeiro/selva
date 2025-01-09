from typing import Annotated

from asgikit.responses import respond_text
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from selva.di import Inject
from selva.web import get


@get
async def index(request, sessionmaker: Annotated[async_sessionmaker, Inject]):
    async with sessionmaker() as session:
        result = await session.execute(text("select sqlite_version()"))
        version = result.first()[0]

    await respond_text(request.response, version)
