import asyncio

from selva.web import RequestContext, controller, get
from selva.web.responses import JSONResponse, BackgroundTask


@controller
class Controller:
    @get
    def background_task(self, context: RequestContext) -> JSONResponse:
        name = context.query.get("name", "World")
        message = f"Hello, {name}!"
        return JSONResponse({"message": message}, background=BackgroundTask(self.say_message, message))

    async def say_message(self, message: str):
        await asyncio.sleep(5)
        print(message)
