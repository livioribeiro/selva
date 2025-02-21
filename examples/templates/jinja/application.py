from typing import Annotated as A

from selva.di import Inject
from selva.web import Request, get
from selva.ext.templates.jinja import JinjaTemplate


@get
async def index(request: Request, template: A[JinjaTemplate, Inject]):
    context = dict(title="Selva", heading="Heading")
    await template.respond(request, "index.html", context)
