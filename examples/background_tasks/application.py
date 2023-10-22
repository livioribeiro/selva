import asyncio

from asgikit.requests import Request
from asgikit.responses import respond_json

from selva.web import controller, get


@controller
class Controller:
    @get
    async def background_task(self, request: Request):
        name = request.query.get("name", "World")
        message = f"Hello, {name}!"

        await respond_json(request.response, {"message": message})

        await asyncio.sleep(5)
        print(message)
