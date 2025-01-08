from typing import Annotated

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import get


@get("/render")
async def render(request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(
        request.response,
        "template.html",
        {"variable": "Jinja"},
    )


@get("/stream")
async def stream(request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(
        request.response,
        "template.html",
        {"variable": "Jinja"},
        stream=True,
    )


@get("/define_content_type")
async def define_content_type(request, template: Annotated[JinjaTemplate, Inject]):
    await template.respond(
        request.response,
        "template.html",
        {"variable": "Jinja"},
        content_type="text/defined",
    )


@get("/override_content_type")
async def override_content_type(request, template: Annotated[JinjaTemplate, Inject]):
    request.response.content_type = "text/plain"

    await template.respond(
        request.response,
        "template.html",
        {"variable": "Jinja"},
        content_type="text/overriden",
    )


@get("/content_type_from_response")
async def content_type_from_response(
    request, template: Annotated[JinjaTemplate, Inject]
):
    request.response.content_type = "text/from_response"

    await template.respond(
        request.response,
        "template.html",
        {"variable": "Jinja"},
    )
