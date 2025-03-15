import asyncio

import structlog

from selva.web import Request, get

logger = structlog.get_logger()


@get
async def background_task(request: Request):
    name = request.query_params.get("name", "World")
    message = f"Hello, {name}!"

    await request.respond({"message": message})

    await asyncio.sleep(5)
    logger.info(message)
