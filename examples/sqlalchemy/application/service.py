from typing import Annotated

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from selva.di import service, Inject

from .model import Base, MyModel, OtherBase, OtherModel


@service
class DefautDBService:
    engine: Annotated[AsyncEngine, Inject]
    sessionmaker: Annotated[async_sessionmaker, Inject]

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self.sessionmaker() as session:
            my_model = MyModel(name="MyModel")
            session.add(my_model)
            await session.commit()

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT sqlite_version()"))

    async def get_model(self) -> MyModel:
        async with self.sessionmaker() as session:
            return await session.scalar(select(MyModel).limit(1))


@service
class OtherDBService:
    engine: Annotated[AsyncEngine, Inject(name="other")]
    sessionmaker: Annotated[async_sessionmaker, Inject]

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(OtherBase.metadata.create_all)

        async with self.sessionmaker() as session:
            my_model = OtherModel(name="OtherModel")
            session.add(my_model)
            await session.commit()

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT version()"))

    async def get_model(self) -> OtherModel:
        async with self.sessionmaker() as session:
            return await session.scalar(select(OtherModel).limit(1))
