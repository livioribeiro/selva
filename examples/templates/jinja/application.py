from typing import Annotated as A

from asgikit.requests import Request

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import get


@get
async def index(request: Request, template: A[JinjaTemplate, Inject]):
    context = dict(title="Selva", heading="Heading")
    await template.respond(request.response, "index.html", context)
