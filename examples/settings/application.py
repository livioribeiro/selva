from typing import Annotated as A

from selva.conf import Settings
from selva.di import Inject
from selva.web import get
from selva.web.http import Request


@get
async def index(request: Request, settings: A[Settings, Inject]):
    await request.respond(settings.message)
