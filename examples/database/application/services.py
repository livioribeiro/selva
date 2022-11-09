import os

from databases import Database

from selva.configuration import Settings
from selva.di import Inject, service


@service
def database_factory(settings: Settings) -> Database:
    database = Database(settings.DATABASE_URL)
    print("Sqlite database created")

    yield database

    os.unlink(database.url.database)
    print("Sqlite database destroyed")


@service
class Repository:
    database: Database = Inject()

    async def initialize(self):
        await self.database.connect()
        print("Sqlite database connection opened")

        await self.database.execute(
            "create table if not exists counter(value int not null)"
        )
        await self.database.execute("insert into counter values (0)")

    async def finalize(self):
        await self.database.disconnect()
        print("Sqlite database connection closed")

    async def test(self):
        await self.database.execute("select 1")

    async def count(self) -> int:
        await self.database.execute("update counter set value = value + 1")
        result = await self.database.fetch_val("select value from counter")
        return result
