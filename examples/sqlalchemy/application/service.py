from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from selva.di import service

from .model import Base, MyModel, OtherBase, OtherModel


@service
async def default_db_service(locator) -> "DefaultDBService":
    engine = await locator.get(AsyncEngine)
    sessionmaker = await locator.get(async_sessionmaker)

    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker() as session:
        my_model = MyModel(name="MyModel")
        session.add(my_model)
        await session.commit()

    return DefaultDBService(engine, sessionmaker)


@service
async def other_db_service(locator) -> "OtherDBService":
    engine = await locator.get(AsyncEngine, name="other")
    sessionmaker = await locator.get(async_sessionmaker)

    async with engine.connect() as conn:
        await conn.run_sync(OtherBase.metadata.create_all)
        await conn.commit()

    async with sessionmaker() as session:
        my_model = OtherModel(name="OtherModel")
        session.add(my_model)
        await session.commit()

    return OtherDBService(engine, sessionmaker)


class DefaultDBService:
    def __init__(self, engine: AsyncEngine, sessionmaker: async_sessionmaker):
        self.engine = engine
        self.sessionmaker = sessionmaker

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT sqlite_version()"))

    async def get_model(self) -> MyModel:
        async with self.sessionmaker() as session:
            return await session.scalar(select(MyModel).limit(1))


class OtherDBService:
    def __init__(self, engine: AsyncEngine, sessionmaker: async_sessionmaker):
        self.engine = engine
        self.sessionmaker = sessionmaker

    async def db_version(self) -> str:
        async with self.engine.connect() as conn:
            return await conn.scalar(text("SELECT version()"))

    async def get_model(self) -> OtherModel:
        async with self.sessionmaker() as session:
            return await session.scalar(select(OtherModel).limit(1))
