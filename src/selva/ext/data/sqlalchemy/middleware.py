from contextvars import ContextVar

from sqlalchemy.ext.asyncio import async_sessionmaker

from selva.configuration.settings import Settings
from selva.di.container import Container

SESSION = ContextVar("session")


async def request_scoped_session(app, settings: Settings, container: Container):
    sessionmaker = await container.get(async_sessionmaker)

    async def middleware(scope, receive, send):
        async with sessionmaker() as session:
            token = SESSION.set(session)
            try:
                await app(scope, receive, send)
            except:
                await session.rollback()
                raise
            finally:
                SESSION.reset(token)

    return middleware