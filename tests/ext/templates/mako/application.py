from typing import Annotated

from selva.di import Inject
from selva.ext.templates.mako import MakoTemplate
from selva.web import Request, get


@get("/render")
async def render(request: Request, template: Annotated[MakoTemplate, Inject]):
    await template.respond(request, "template.html", {"variable": "Mako"})


@get("/content_type")
async def define_content_type(request, template: Annotated[MakoTemplate, Inject]):
    await template.respond(
        request, "template.html", {"variable": "Mako"}, media_type="text/plain"
    )
