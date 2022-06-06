from pathlib import Path

import asyncpg

from selva.di import Scope, finalizer, service

BASE_PATH = Path(__file__).resolve().parent


async def finalize_database_pool(pool: asyncpg.Pool):
    await pool.close()
    print("Postgres connection pool closed")


@service
@finalizer(finalize_database_pool)
async def database_pool_factory() -> asyncpg.Pool:
    print("Postgres creating connection pool")
    return await asyncpg.create_pool(user="postgres", password="postgres")


async def database_connection_finalizer(connection: asyncpg.pool.PoolConnectionProxy):
    await connection._holder.release(5)
    print("Postgres database connection released")


@service(scope=Scope.TRANSIENT)
@finalizer(database_connection_finalizer)
async def database_connection_factory(pool: asyncpg.Pool) -> asyncpg.Connection:
    print("Postgres acquiring database connection")
    return await pool.acquire()
