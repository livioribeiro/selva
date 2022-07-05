from selva.web import RequestContext

ASGI_SCOPE = {
    "type": "http",
    "http_version": "1.1",
    "method": "GET",
}


async def test_sync_tasks():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = False

    def task():
        nonlocal result
        result = True

    ctx.add_delayed_task(task)
    for task in ctx.delayed_tasks:
        await task

    assert result


async def test_async_tasks():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = False

    async def task():
        nonlocal result
        result = True

    ctx.add_delayed_task(task)
    for task in ctx.delayed_tasks:
        await task

    assert result


async def test_awaitable_tasks():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = False

    async def task():
        nonlocal result
        result = True

    ctx.add_delayed_task(task())
    for task in ctx.delayed_tasks:
        await task

    assert result


async def test_sync_tasks_with_args():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None

    def task(arg):
        nonlocal result
        result = arg

    ctx.add_delayed_task(task, "arg")
    for task in ctx.delayed_tasks:
        await task

    assert result == "arg"


async def test_async_tasks_with_args():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None

    async def task(arg):
        nonlocal result
        result = arg

    ctx.add_delayed_task(task, "arg")
    for task in ctx.delayed_tasks:
        await task

    assert result == "arg"


async def test_sync_tasks_with_kwargs():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None

    def task(*, kwarg):
        nonlocal result
        result = kwarg

    ctx.add_delayed_task(task, kwarg="kwarg")
    for task in ctx.delayed_tasks:
        await task

    assert result == "kwarg"


async def test_async_tasks_with_kwargs():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None

    async def task(*, kwarg):
        nonlocal result
        result = kwarg

    ctx.add_delayed_task(task, kwarg="kwarg")
    for task in ctx.delayed_tasks:
        await task

    assert result == "kwarg"


async def test_sync_tasks_with_args_and_kwargs():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None, None

    def task(arg, *, kwarg):
        nonlocal result
        result = arg, kwarg

    ctx.add_delayed_task(task, "arg", kwarg="kwarg")
    for task in ctx.delayed_tasks:
        await task

    assert result == ("arg", "kwarg")


async def test_async_tasks_with_args_and_kwargs():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result = None, None

    async def task(arg, *, kwarg):
        nonlocal result
        result = arg, kwarg

    ctx.add_delayed_task(task, "arg", kwarg="kwarg")
    for task in ctx.delayed_tasks:
        await task

    assert result == ("arg", "kwarg")


async def test_multiple_tasks():
    ctx = RequestContext(ASGI_SCOPE, None, None)

    result1 = None
    result2 = None
    result3 = None

    def sync_task(arg):
        nonlocal result1
        result1 = arg

    async def async_task(arg):
        nonlocal result2
        result2 = arg

    async def coro_task():
        nonlocal result3
        result3 = "value3"

    ctx.add_delayed_task(sync_task, "value1")
    ctx.add_delayed_task(async_task, "value2")
    ctx.add_delayed_task(coro_task())

    for task in ctx.delayed_tasks:
        await task

    assert result1 == "value1"
    assert result2 == "value2"
    assert result3 == "value3"
