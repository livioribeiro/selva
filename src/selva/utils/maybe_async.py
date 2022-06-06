import asyncio
from collections.abc import Callable
from typing import Any


async def call_maybe_async(func: Callable, *args, **kwargs) -> Any:
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)

    return await asyncio.to_thread(func, *args, **kwargs)
