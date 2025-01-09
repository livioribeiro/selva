from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import get, post

click_count = 0


@get
async def index(request: Request, template: A[JinjaTemplate, Inject]):
    global click_count
    await template.respond(request.response, "index.html", {"click_count": click_count})


@post("/clicked")
async def clicked(request: Request, template: A[JinjaTemplate, Inject]):
    global click_count

    click_count += 1

    rendered = await template.render("click-count.html", {"click_count": click_count})

    await respond_text(request.response, rendered + "Clicked!")
