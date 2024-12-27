from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.di import Inject
from selva.web import get, post
from selva.web.templates import Template

click_count = 0


@get
async def index(request: Request, template: A[Template, Inject]):
    global click_count
    await template.respond(request.response, "index.html", {"click_count": click_count})


@post("/clicked")
async def clicked(request: Request, template: A[Template, Inject]):
    global click_count

    click_count += 1

    rendered = await template.render(
        "click-count.html",
        {"click_count": click_count}
    )

    await respond_text(request.response, rendered + "Clicked!")
