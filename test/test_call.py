import pytest

from dependency_injector.errors import CalledNonCallableError

from . import ioc
from .services import call as module
from .utils import Context

pytestmark = pytest.mark.asyncio


async def test_call_function(ioc):
    ioc.scan(module)

    def func(service1: module.Service1):
        return service1

    result = await ioc.call(func)
    assert isinstance(result, module.Service1)


async def test_call_async_function(ioc):
    ioc.scan(module)

    async def func(service1: module.Service1):
        return service1

    result = await ioc.call(func)
    assert isinstance(result, module.Service1)


async def test_call_function_multipe_services(ioc):
    ioc.scan(module)

    def func(service1: module.Service1, service2: module.Service2):
        return service1, service2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, module.Service1)
    assert isinstance(service2, module.Service2)


async def test_call_async_function_multipe_services(ioc):
    ioc.scan(module)

    async def func(service1: module.Service1, service2: module.Service2):
        return service1, service2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, module.Service1)
    assert isinstance(service2, module.Service2)


async def test_call_function_kwargs(ioc):
    ioc.scan(module)

    def func(service1: module.Service1, a):
        return service1, a

    service1, a = await ioc.call(func, kwargs={"a": 1})
    assert isinstance(service1, module.Service1)
    assert a == 1


async def test_call_async_function_kwargs(ioc):
    ioc.scan(module)

    async def func(service1: module.Service1, a):
        return service1, a

    service1, a = await ioc.call(func, kwargs={"a": 1})
    assert isinstance(service1, module.Service1)
    assert a == 1


async def test_call_function_args(ioc):
    ioc.scan(module)

    def func(a, service1: module.Service1):
        return a, service1

    a, service1 = await ioc.call(func, args=[1])
    assert isinstance(service1, module.Service1)
    assert a == 1


async def test_call_async_function_args(ioc):
    ioc.scan(module)

    async def func(a, service1: module.Service1):
        return a, service1

    a, service1 = await ioc.call(func, args=[1])
    assert isinstance(service1, module.Service1)
    assert a == 1


async def test_call_function_args_keyword_only(ioc):
    ioc.scan(module)

    def func1(service1: module.Service1, *, a: int):
        return service1, a

    def func2(a: int, *, service2: module.Service2):
        return a, service2

    result1, a1 = await ioc.call(func1, kwargs={"a": 1})
    a2, result2 = await ioc.call(func2, kwargs={"a": 2})

    assert isinstance(result1, module.Service1)
    assert a1 == 1

    assert isinstance(result2, module.Service2)
    assert a2 == 2


async def test_call_async_function_args_keyword_only(ioc):
    ioc.scan(module)

    async def func1(service1: module.Service1, *, a: int):
        return service1, a

    async def func2(a: int, *, service2: module.Service2):
        return a, service2

    result1, a1 = await ioc.call(func1, kwargs={"a": 1})
    a2, result2 = await ioc.call(func2, kwargs={"a": 2})

    assert isinstance(result1, module.Service1)
    assert a1 == 1

    assert isinstance(result2, module.Service2)
    assert a2 == 2


async def test_call_function_param_after_dependencies_should_fail(ioc):
    ioc.scan(module)

    def func(a, service1: module.Service1):
        pass

    with pytest.raises(Exception):
        ioc.call(func, [1])


async def test_call_async_function_param_after_dependencies_should_fail(ioc):
    ioc.scan(module)

    async def func(a, service1: module.Service1):
        pass

    with pytest.raises(Exception):
        ioc.call(func, [1])


async def test_call_function_with_context(ioc):
    ioc.scan(module)

    def func(service: module.ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, module.ServiceDependent)
    assert id(context) in ioc.store_dependent


async def test_call_async_function_with_context(ioc):
    ioc.scan(module)

    async def func(service: module.ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, module.ServiceDependent)
    assert id(context) in ioc.store_dependent


async def test_call_callable_object(ioc):
    ioc.scan(module)

    class CallableClass:
        def __call__(self, service: module.Service1):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, module.Service1)


async def test_call_async_callable_object(ioc):
    ioc.scan(module)

    class CallableClass:
        async def __call__(self, service: module.Service1):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, module.Service1)


async def test_call_non_callable_object_should_fail(ioc):
    class NonCallableClass:
        pass

    non_callable_object = NonCallableClass()

    with pytest.raises(CalledNonCallableError):
        await ioc.call(non_callable_object)
