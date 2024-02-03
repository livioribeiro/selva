from typing import Annotated

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from asgikit.responses import respond_text
from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    sessionmaker: Annotated[async_sessionmaker, Inject]
    other_sessionmaker: Annotated[async_sessionmaker, Inject(name="other")]

    @get
    async def index(self, request):
        async with self.sessionmaker() as session:
            result = await session.execute(text("select 1"))
            print(result.scalar())
            await session.commit()

        await respond_text(request.response, "Hello World!")

    @get("other")
    async def other(self, request):
        async with self.other_sessionmaker() as session:
            result = await session.execute(text("select 1"))
            print(result.scalar())
            await session.commit()

        await respond_text(request.response, "Hello World!")
