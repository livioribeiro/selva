import asyncio

from asgikit.requests import Request
from asgikit.responses import respond_json
import structlog

from selva.web import controller, get

logger = structlog.get_logger()


@controller
class Controller:
    @get
    async def background_task(self, request: Request):
        name = request.query.get("name", "World")
        message = f"Hello, {name}!"

        await respond_json(request.response, {"message": message})

        await asyncio.sleep(5)
        logger.info(message)
