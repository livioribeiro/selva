import asyncio
import inspect
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any


async def maybe_async(target: Awaitable | Callable | Coroutine, *args, **kwargs) -> Any:
    if inspect.isawaitable(target):
        return await target

    if inspect.iscoroutinefunction(target):
        return await target(*args, **kwargs)

    return await asyncio.to_thread(target, *args, **kwargs)
