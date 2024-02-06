from typing import Annotated

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from asgikit.responses import respond_text
from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    sessionmaker: Annotated[async_sessionmaker, Inject]

    @get
    async def index(self, request):
        async with self.sessionmaker() as session:
            result = await session.execute(text("select sqlite_version()"))
            version = result.first()[0]

        await respond_text(request.response, version)