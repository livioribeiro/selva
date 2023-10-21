from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.configuration import Settings
from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    settings: Annotated[Settings, Inject]

    @get
    async def index(self, request: Request):
        await respond_text(request.response, self.settings.MESSAGE)
