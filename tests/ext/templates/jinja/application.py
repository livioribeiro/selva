from typing import Annotated

from selva.di import Inject
from selva.web import controller, get
from selva.web.templates import Template


@controller
class Controller:
    template: Annotated[Template, Inject]

    @get("/render")
    async def render(self, request):
        await self.template.respond(
            request.response,
            "template.html",
            {"variable": "Jinja"},
        )

    @get("/stream")
    async def stream(self, request):
        await self.template.respond(
            request.response,
            "template.html",
            {"variable": "Jinja"},
            stream=True,
        )

    @get("/define_content_type")
    async def define_content_type(self, request):
        await self.template.respond(
            request.response,
            "template.html",
            {"variable": "Jinja"},
            content_type="text/defined",
        )

    @get("/override_content_type")
    async def override_content_type(self, request):
        request.response.content_type = "text/plain"

        await self.template.respond(
            request.response,
            "template.html",
            {"variable": "Jinja"},
            content_type="text/overriden",
        )

    @get("/content_type_from_response")
    async def content_type_from_response(self, request):
        request.response.content_type = "text/from_response"

        await self.template.respond(
            request.response,
            "template.html",
            {"variable": "Jinja"},
        )
