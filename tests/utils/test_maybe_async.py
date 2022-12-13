import pytest

from selva._utils.maybe_async import maybe_async


async def test_awaitable_object():
    async def func():
        return 1

    awaitable = func()
    result = await maybe_async(awaitable)
    assert result == 1


async def test_not_callable_should_fail():
    not_callable = None

    with pytest.raises(TypeError):
        await maybe_async(not_callable)


async def test_call_async_function():
    async def func():
        return 1

    result = await maybe_async(func)
    assert result == 1


async def test_call_async_function_with_args():
    async def func(param: int):
        return param

    result = await maybe_async(func, 1)
    assert result == 1


async def test_call_async_function_with_kwargs():
    async def func(param: int):
        return param

    result = await maybe_async(func, param=1)
    assert result == 1


async def test_call_async_method():
    class Klass:
        async def func(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj.func)
    assert result == 1


async def test_call_async_method_with_args():
    class Klass:
        async def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, 1)
    assert result == 1


async def test_call_async_method_with_kwargs():
    class Klass:
        async def func(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj.func, param=1)
    assert result == 1


async def test_call_async_object():
    class Klass:
        async def __call__(self):
            return 1

    obj = Klass()

    result = await maybe_async(obj)
    assert result == 1


async def test_call_async_object_with_args():
    class Klass:
        async def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, 1)
    assert result == 1


async def test_call_async_object_with_kwargs():
    class Klass:
        async def __call__(self, param: int):
            return param

    obj = Klass()

    result = await maybe_async(obj, param=1)
    assert result == 1
