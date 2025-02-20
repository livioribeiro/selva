from typing import Annotated

from jinja2 import Template

from selva.di import Inject
from selva.web import Request, HTMLResponse, StreamingResponse, get


@get("/render")
async def render(request: Request, template: Annotated[Template, Inject("template.html")]):
    response = await template.render_async({"variable": "Jinja"})
    await request.respond(HTMLResponse(response))


@get("/stream")
async def stream(request: Request, template: Annotated[Template, Inject("template.html")]):
    response = template.stream({"variable": "Jinja"})
    await request.respond(StreamingResponse(response, content_type="text/html"))


@get("/content_type")
async def define_content_type(
    request: Request, template: Annotated[Template, Inject("template.html")]
):
    response = await template.render_async({"variable": "Jinja"})
    await request.respond(HTMLResponse(response, content_type="text/plain"))
