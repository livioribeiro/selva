import functools
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec

import anyio

P = ParamSpec("P")


async def maybe_async(
    target: Awaitable | Callable[P, Any], *args: P.args, **kwargs: P.kwargs
) -> Any:
    if inspect.isawaitable(target):
        return await target

    if not callable(target):
        raise TypeError(f"{repr(target)} is not callable")

    call = target if inspect.isroutine(target) else getattr(target, "__call__")

    if inspect.iscoroutinefunction(call):
        return await call(*args, **kwargs)

    blocking = getattr(call, "_blocking_", False)
    if blocking:
        target = functools.partial(target, *args, **kwargs)
        return await anyio.to_thread.run_sync(target)

    return call(*args, **kwargs)
