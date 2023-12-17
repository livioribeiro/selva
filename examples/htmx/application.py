from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.di import Inject
from selva.web import controller, get, post
from selva.web.templates import Template


@controller
class Controller:
    template: Annotated[Template, Inject]

    click_count = 0

    @get
    async def index(self, request: Request):
        await self.template.respond(request.response, "index.html", {"click_count": self.click_count})

    @post("/clicked")
    async def clicked(self, request: Request):
        self.click_count += 1
        await self.template.respond(request.response, "clicked.html", {"click_count": self.click_count})
