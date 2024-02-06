from typing import Annotated

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from asgikit.responses import respond_json
from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    sessionmaker: Annotated[async_sessionmaker, Inject]
    other_sessionmaker: Annotated[async_sessionmaker, Inject(name="other")]

    @get
    async def index(self, request):
        async with self.sessionmaker() as session:
            result = await session.execute(text("SELECT sqlite_version()"))
            sqlite_version = result.scalar()

        await respond_json(request.response, {"sqlite_version": sqlite_version})

    @get("other")
    async def other(self, request):
        async with self.other_sessionmaker() as session:
            result = await session.stream_scalars(text("SELECT version()"))
            postgres_version = await result.first()

        await respond_json(request.response, {"postgres_version": postgres_version})
