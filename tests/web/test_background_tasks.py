from selva.web.background_tasks import BackgroundTasks


async def test_sync_tasks():
    bt = BackgroundTasks()

    result = False

    def task():
        nonlocal result
        result = True

    bt.add_task(task)
    await bt._run_tasks()
    assert result


async def test_async_tasks():
    bt = BackgroundTasks()

    result = False

    async def task():
        nonlocal result
        result = True

    bt.add_task(task)
    await bt._run_tasks()
    assert result


async def test_awaitable_tasks():
    bt = BackgroundTasks()

    result = False

    async def task():
        nonlocal result
        result = True

    bt.add_task(task())
    await bt._run_tasks()
    assert result


async def test_sync_tasks_with_args():
    bt = BackgroundTasks()

    result = None

    def task(arg):
        nonlocal result
        result = arg

    bt.add_task(task, "arg")
    await bt._run_tasks()
    assert result == "arg"


async def test_async_tasks_with_args():
    bt = BackgroundTasks()

    result = None

    async def task(arg):
        nonlocal result
        result = arg

    bt.add_task(task, "arg")
    await bt._run_tasks()
    assert result == "arg"


async def test_sync_tasks_with_kwargs():
    bt = BackgroundTasks()

    result = None

    def task(*, kwarg):
        nonlocal result
        result = kwarg

    bt.add_task(task, kwarg="kwarg")
    await bt._run_tasks()
    assert result == "kwarg"


async def test_async_tasks_with_kwargs():
    bt = BackgroundTasks()

    result = None

    async def task(*, kwarg):
        nonlocal result
        result = kwarg

    bt.add_task(task, kwarg="kwarg")
    await bt._run_tasks()
    assert result == "kwarg"


async def test_sync_tasks_with_args_and_kwargs():
    bt = BackgroundTasks()

    result = None, None

    def task(arg, *, kwarg):
        nonlocal result
        result = arg, kwarg

    bt.add_task(task, "arg", kwarg="kwarg")
    await bt._run_tasks()
    assert result == ("arg", "kwarg")


async def test_async_tasks_with_args_and_kwargs():
    bt = BackgroundTasks()

    result = None, None

    async def task(arg, *, kwarg):
        nonlocal result
        result = arg, kwarg

    bt.add_task(task, "arg", kwarg="kwarg")
    await bt._run_tasks()
    assert result == ("arg", "kwarg")


async def test_multiple_tasks():
    bt = BackgroundTasks()

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

    bt.add_task(sync_task, "value1")
    bt.add_task(async_task, "value2")
    bt.add_task(coro_task())

    await bt._run_tasks()
    assert result1 == "value1"
    assert result2 == "value2"
    assert result3 == "value3"
