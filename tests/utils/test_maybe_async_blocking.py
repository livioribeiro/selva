from selva._utils.maybe_async import maybe_async
from selva.decorators import blocking


async def test_call_blocking_function():
    @blocking
    def func():
        return 1

    result = await maybe_async(func)
    assert result == 1


async def test_call_blocking_function_with_args():
    @blocking
    def func(param: int):
        return param

    result = await maybe_async(func, 1)
    assert result == 1


async def test_call_blocking_function_with_kwargs():
    @blocking
    def func(param: int):
        return param

    result = await maybe_async(func, param=1)
    assert result == 1


async def test_call_blocking_method():
    class Klass:
        @blocking
        def func(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj.func)
    assert result == 1


async def test_call_blocking_method_with_args():
    class Klass:
        @blocking
        def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, 1)
    assert result == 1


async def test_call_blocking_method_with_kwargs():
    class Klass:
        @blocking
        def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, param=1)
    assert result == 1


async def test_call_blocking_object():
    class Klass:
        @blocking
        def __call__(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj)
    assert result == 1


async def test_call_blocking_object_with_args():
    class Klass:
        @blocking
        def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, 1)
    assert result == 1


async def test_call_blocking_object_with_kwargs():
    class Klass:
        @blocking
        def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, param=1)
    assert result == 1
