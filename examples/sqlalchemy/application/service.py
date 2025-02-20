from typing import Annotated as A

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from selva.di import Inject, service
from selva.ext.data.sqlalchemy.service import ScopedSession

from .model import Base, MyModel, OtherBase, OtherModel


@service
class DefaultDBService:
    engine: A[AsyncEngine, Inject]
    sessionmaker: A[async_sessionmaker, Inject]
    session: A[ScopedSession, Inject]

    async def initialize(self):
        async with self.engine.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self.sessionmaker() as session:
            my_model = MyModel(name="MyModel")
            session.add(my_model)
            await session.commit()

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT sqlite_version()"))

    async def get_model(self) -> MyModel:
        return await self.session.scalar(select(MyModel).limit(1))


@service
class OtherDBService:
    engine: A[AsyncEngine, Inject("other")]
    sessionmaker: A[async_sessionmaker, Inject]
    session: A[ScopedSession, Inject]

    async def initialize(self):
        async with self.engine.connect() as conn:
            await conn.run_sync(OtherBase.metadata.create_all)
            await conn.commit()

        async with self.sessionmaker() as session:
            my_model = OtherModel(name="OtherModel")
            session.add(my_model)
            await session.commit()

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT version()"))

    async def get_model(self) -> OtherModel:
        return await self.session.scalar(select(OtherModel).limit(1))
