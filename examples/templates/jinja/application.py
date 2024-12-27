from typing import Annotated as A

from asgikit.requests import Request

from selva.di import Inject
from selva.web import get
from selva.web.templates import Template


@get
async def index(request: Request, template: A[Template, Inject]):
    context = dict(title="Selva", heading="Heading")
    await template.respond(request.response, "index.html", context)
