from typing import Annotated as A

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import get
from selva.web.http import Request


@get
async def index(request: Request, template: A[JinjaTemplate, Inject]):
    context = dict(title="Selva", heading="Heading")
    response = await template.response("index.html", context)
    await request.respond(response)
