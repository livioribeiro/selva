from typing import Annotated

from asgikit.requests import Request

from selva.di import Inject
from selva.web import controller, get
from selva.web.templates import Template


@controller
class Controller:
    template: Annotated[Template, Inject]

    @get
    async def index(self, request: Request):
        context = dict(title="Selva", heading="Heading")
        await self.template.respond(request.response, "index.html", context)
