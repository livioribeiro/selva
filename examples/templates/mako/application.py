from typing import Annotated as A

from selva.di import Inject
from selva.ext.templates.mako import MakoTemplate
from selva.web import Request, get


@get
async def index(request: Request, template: A[MakoTemplate, Inject]):
    context = {
        "title": "Selva",
        "heading": "Heading",
        "data": [
            {"name": "Item 1", "number": 111},
            {"name": "Item 2", "number": 222},
            {"name": "Item 3", "number": 333},
        ],
    }

    response = await template.response("index.html", context)
    await request.respond(response)
