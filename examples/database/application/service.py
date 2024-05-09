import os
from typing import Annotated

from databases import Database
import structlog

from selva.configuration import Settings
from selva.di import Inject, service

logger = structlog.get_logger()


@service
def database_factory(settings: Settings) -> Database:
    database = Database(settings.database.url)
    logger.info("sqlite database created")

    yield database

    os.unlink(database.url.database)
    logger.info("sqlite database destroyed")


@service
class Repository:
    database: Annotated[Database, Inject]

    async def initialize(self):
        await self.database.connect()
        logger.info("sqlite database connection opened")

        await self.database.execute(
            "create table if not exists counter(value int not null)"
        )
        await self.database.execute("insert into counter values (0)")

    async def finalize(self):
        await self.database.disconnect()
        logger.info("sqlite database connection closed")

    async def test(self):
        await self.database.execute("select 1")

    async def count(self) -> int:
        await self.database.execute("update counter set value = value + 1")
        result = await self.database.fetch_val("select value from counter")
        logger.info("count updated", count=result)
        return result
