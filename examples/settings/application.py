from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.configuration import Settings
from selva.di import Inject
from selva.web import get


@get
async def index(request: Request, settings: A[Settings, Inject]):
    await respond_text(request.response, settings.message)
