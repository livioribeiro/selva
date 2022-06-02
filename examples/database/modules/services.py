from pathlib import Path

from databases import Database

from selva.di import service, initializer, finalizer

BASE_PATH = Path(__file__).resolve().parent


@service
def database_factory() -> Database:
    return Database(f"sqlite+aiosqlite:///{BASE_PATH}/db.sqlite3")


@service
class Repository:
    def __init__(self, database: Database):
        self.database = database

    async def test(self):
        await self.database.execute("select 1")

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Database connection opened")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Database connection closed")