from typing import Annotated

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import Request, get


@get("/render")
async def render(request: Request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(request, "template.html", {"variable": "Jinja"})


@get("/stream")
async def stream(request: Request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(
        request,
        "template.html",
        {"variable": "Jinja"},
        stream=True,
    )


@get("/content_type")
async def content_type(request: Request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(
        request,
        "template.html",
        {"variable": "Jinja"},
        content_type="text/plain",
    )
