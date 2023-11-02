from selva._util.maybe_async import maybe_async


async def test_call_sync_function():
    def func():
        return 1

    result = await maybe_async(func)
    assert result == 1


async def test_call_sync_function_with_args():
    def func(param: int):
        return param

    result = await maybe_async(func, 1)
    assert result == 1


async def test_call_sync_function_with_kwargs():
    def func(param: int):
        return param

    result = await maybe_async(func, param=1)
    assert result == 1


async def test_call_sync_method():
    class Klass:
        def func(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj.func)
    assert result == 1


async def test_call_sync_method_with_args():
    class Klass:
        def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, 1)
    assert result == 1


async def test_call_sync_method_with_kwargs():
    class Klass:
        def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, param=1)
    assert result == 1


async def test_call_sync_object():
    class Klass:
        def __call__(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj)
    assert result == 1


async def test_call_sync_object_with_args():
    class Klass:
        def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, 1)
    assert result == 1


async def test_call_sync_object_with_kwargs():
    class Klass:
        def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, param=1)
    assert result == 1
