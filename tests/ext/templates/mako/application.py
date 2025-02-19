from typing import Annotated

from selva.di import Inject
from selva.ext.templates.mako import MakoTemplate
from selva.web import Request, get


@get("/render")
async def render(request: Request, template: Annotated[MakoTemplate, Inject]):
    response = await template.response("template.html", {"variable": "Mako"})
    await request.respond(response)


@get("/content_type")
async def define_content_type(request, template: Annotated[MakoTemplate, Inject]):
    response = await template.response(
        "template.html", {"variable": "Mako"}, content_type="text/plain"
    )
    await request.respond(response)
