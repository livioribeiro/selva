import os

from databases import Database
import structlog

from selva.configuration import Settings
from selva.di import service

logger = structlog.get_logger()


@service
async def database_factory(locator) -> Database:
    settings = await locator.get(Settings)
    database = Database(settings.database.url)
    logger.info("sqlite database created")

    yield database

    os.unlink(database.url.database)
    logger.info("sqlite database destroyed")


@service
async def database_repository(locator) -> "Repository":
    database = await locator.get(Database)
    await database.connect()
    logger.info("sqlite database connection opened")

    await database.execute("create table if not exists counter(value int not null)")
    await database.execute("insert into counter values (0)")

    yield Repository(database)

    await database.disconnect()
    logger.info("sqlite database connection closed")


class Repository:
    def __init__(self, database: Database):
        self.database = database

    async def test(self):
        await self.database.execute("select 1")

    async def count(self) -> int:
        await self.database.execute("update counter set value = value + 1")
        result = await self.database.fetch_val("select value from counter")
        logger.info("count updated", count=result)
        return result
