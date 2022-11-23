import asyncio

from selva.web import RequestContext, controller, get
from selva.web.responses import JSONResponse

from starlette.background import BackgroundTask


@controller
class Controller:
    @get
    def index(self, context: RequestContext):
        name = context.query.get("name", "World")
        message = f"Hello, {name}!"
        context.add_delayed_task(self.say_message, message)
        # return {"message": message}
        return JSONResponse({"message": message}, background=BackgroundTask(self.say_message, message))

    async def say_message(self, message: str):
        await asyncio.sleep(5)
        print(message)
