import asyncio

from starlette.background import BackgroundTask

from selva.web import RequestContext, controller, get
from selva.web.responses import JSONResponse


@controller
class Controller:
    @get
    def index(self, context: RequestContext) -> dict:
        name = context.query.get("name", "World")
        message = f"Hello, {name}!"
        context.add_delayed_task(self.say_message, message)
        return {"message": message}

    async def say_message(self, message: str):
        await asyncio.sleep(5)
        print(message)
