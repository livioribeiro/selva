from typing import Annotated

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from selva.di import service, Inject

from .model import Base, MyModel


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
        async with self.sessionmaker() as session:
            result = await session.execute(text("SELECT sqlite_version()"))
            return result.scalar()

    async def get_model(self) -> MyModel:
        async with self.sessionmaker() as session:
            result = await session.execute(select(MyModel))
            return result.scalar()


@service
class OtherDBService:
    sessionmaker: Annotated[async_sessionmaker, Inject(name="other")]

    async def db_version(self) -> str:
        async with self.sessionmaker() as session:
            result = await session.execute(text("SELECT version()"))
            return result.scalar()
