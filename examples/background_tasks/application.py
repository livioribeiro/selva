import asyncio

from asgikit.requests import Request
from asgikit.responses import Response, respond_json

from selva.web import controller, get


@controller
class Controller:
    @get
    async def background_task(self, request: Request, response: Response):
        name = request.query.get("name", "World")
        message = f"Hello, {name}!"

        await respond_json(response, {"message": message})

        await asyncio.sleep(5)
        print(message)
