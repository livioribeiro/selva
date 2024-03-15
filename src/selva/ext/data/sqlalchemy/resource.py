from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncConnection, AsyncEngine

from selva.di.inject import Inject


def make_session_resource(name: str):
    def session_resource(
        sessionmaker: Annotated[async_sessionmaker, Inject(name=name)],
    ) -> AsyncSession:
        return sessionmaker()

    return session_resource


def make_connection_resource(name: str):
    def session_resource(
        engine: Annotated[AsyncEngine, Inject(name=name)],
    ) -> AsyncConnection:
        return engine.connect()

    return session_resource

