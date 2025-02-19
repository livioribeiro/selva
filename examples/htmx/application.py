from typing import Annotated as A

from selva.di import Inject
from selva.ext.templates.jinja import JinjaTemplate
from selva.web import Request, get, post

import structlog

logger = structlog.get_logger()

click_count = 0


@get
async def index(request: Request, template: A[JinjaTemplate, Inject]):
    global click_count
    response = await template.response("index.html", {"click_count": click_count})
    await request.respond(response)
    logger.warning("index", click_count=click_count)


@post("/clicked")
async def clicked(request: Request, template: A[JinjaTemplate, Inject]):
    global click_count

    click_count += 1

    rendered = await template.render("click-count.html", {"click_count": click_count})

    await request.respond(rendered + "Clicked!")

    logger.info("clicked", click_count=click_count)
