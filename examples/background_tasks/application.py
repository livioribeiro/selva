import asyncio

from selva.web import controller, get, RequestContext
from selva.web.background_tasks import BackgroundTasks


@controller
class Controller:
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    @get
    def index(self, context: RequestContext):
        name = context.query.get("name", "World")
        message = f"Hello, {name}!"
        self.background_tasks.add_task(self.say_message, message)
        return {"message": message}

    async def say_message(self, message: str):
        await asyncio.sleep(5)
        print(message)
