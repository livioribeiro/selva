from typing import Annotated

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import Request, get


@get("/render")
async def render(request: Request, template: Annotated[JinjaTemplate, Inject]):
    response = await template.response("template.html", {"variable": "Jinja"})
    await request.respond(response)


@get("/stream")
async def stream(request: Request, template: Annotated[JinjaTemplate, Inject]):
    response = await template.response(
        "template.html",
        {"variable": "Jinja"},
        stream=True,
    )
    await request.respond(response)


@get("/content_type")
async def define_content_type(
    request: Request, template: Annotated[JinjaTemplate, Inject]
):
    response = await template.response(
        "template.html",
        {"variable": "Jinja"},
        content_type="text/plain",
    )
    await request.respond(response)
