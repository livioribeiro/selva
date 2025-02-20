from typing import Annotated as A

from jinja2 import Template

from selva.di import Inject
from selva.web import Request, HTMLResponse, get


@get
async def index(request: Request, template: A[Template, Inject("index.html")]):
    context = dict(title="Selva", heading="Heading")
    response = await template.render_async(**context)
    await request.respond(HTMLResponse(response))
