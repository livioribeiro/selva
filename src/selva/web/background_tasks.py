import asyncio
from collections.abc import Awaitable, Callable
from functools import partial

from selva.di import Scope, finalizer, service
from selva.utils.maybe_async import maybe_async


@service(scope=Scope.DEPENDENT)
class BackgroundTasks:
    def __init__(self):
        self._tasks = []

    def add_task(self, task: Callable | Awaitable, *args, **kwargs):
        if asyncio.iscoroutine(task) or not (args or kwargs):
            self._tasks.append(task)
        elif asyncio.iscoroutinefunction(task):
            self._tasks.append(task(*args, **kwargs))
        else:
            self._tasks.append(partial(task, *args, **kwargs))

    @finalizer
    async def _run_tasks(self):
        for task in self._tasks:
            await maybe_async(task)
