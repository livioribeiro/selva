from typing import Annotated

from asgikit.responses import respond_text
from sqlalchemy import text

from selva.di import Inject, service
from selva.ext.data.sqlalchemy import ScopedSession
from selva.web import get


@service
class MyService:
    session: Annotated[ScopedSession, Inject]

    async def select(self):
        return await self.session.scalar(text("select 1"))


@get
async def index(request, my_service: Annotated[MyService, Inject]):
    value = await my_service.select()
    await respond_text(request.response, str(value))
