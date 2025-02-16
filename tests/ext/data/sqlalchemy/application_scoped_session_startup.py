from sqlalchemy import text

from selva.ext.data.sqlalchemy import ScopedSession
from selva.web import startup


@startup
async def startup(session: ScopedSession):
    await session.scalar(text("select 1"))
