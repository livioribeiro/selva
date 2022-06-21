import asyncio
import os

from databases import Database

from selva.di import finalizer, initializer, service
from selva.web.configuration import Settings


def database_finalizer(database: Database):
    os.unlink(database.url.database)


@service
@finalizer(database_finalizer)
def database_factory(settings: Settings) -> Database:
    return Database(settings["database:url"])


@service
class Repository:
    def __init__(self, database: Database):
        self.database = database

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Sqlite database connection opened")

        await self.database.execute(
            "create table if not exists counter(value int not null)"
        )
        await self.database.execute("insert into counter values (0)")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Sqlite database connection closed")
        # await asyncio.to_thread(DB_FILE.unlink, missing_ok=True)
        await asyncio.to_thread(self.settings, missing_ok=True)

    async def test(self):
        await self.database.execute("select 1")

    async def count(self) -> int:
        await self.database.execute("update counter set value = value + 1")
        return await self.database.fetch_val("select value from counter")
