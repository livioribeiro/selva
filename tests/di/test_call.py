import pytest

from selva.di import Container, Scope
from selva.di.errors import CalledNonCallableError

from .fixtures import ioc
from .utils import Context


class ServiceSingleton:
    pass


class ServiceTransient:
    pass


class ServiceDependent:
    pass


@pytest.fixture(autouse=True)
async def services(ioc: Container):
    ioc.register(ServiceSingleton, Scope.SINGLETON)
    ioc.register(ServiceTransient, Scope.TRANSIENT)
    ioc.register(ServiceDependent, Scope.DEPENDENT)


async def test_call_function(ioc: Container):
    def func(service: ServiceSingleton):
        return service

    result = await ioc.call(func)
    assert isinstance(result, ServiceSingleton)


async def test_call_async_function(ioc: Container):
    async def func(service: ServiceSingleton):
        return service

    result = await ioc.call(func)
    assert isinstance(result, ServiceSingleton)


async def test_call_function_with_multiple_dependencies(ioc: Container):
    def func(dep1: ServiceSingleton, dep2: ServiceTransient):
        return dep1, dep2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


async def test_call_async_function_with_multipe_dependencies(ioc: Container):
    async def func(service1: ServiceSingleton, service2: ServiceTransient):
        return service1, service2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


async def test_call_function_with_kwargs(ioc: Container):
    def func(service: ServiceSingleton, arg):
        return service, arg

    service, arg = await ioc.call(func, kwargs={"arg": 1})
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


async def test_call_async_function_with_kwargs(ioc: Container):
    async def func(service: ServiceSingleton, arg):
        return service, arg

    service, arg = await ioc.call(func, kwargs={"arg": 1})
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


async def test_call_function_with_args(ioc: Container):
    def func(arg, service: ServiceSingleton):
        return arg, service

    arg, service = await ioc.call(func, args=[1])
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


async def test_call_async_function_with_args(ioc: Container):
    async def func(arg, service: ServiceSingleton):
        return arg, service

    arg, service = await ioc.call(func, args=[1])
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


async def test_call_function_with_keyword_only_args(ioc: Container):
    def func1(service: ServiceSingleton, *, arg: int):
        return service, arg

    def func2(arg: int, *, service: ServiceTransient):
        return arg, service

    service1, arg1 = await ioc.call(func1, kwargs={"arg": 1})
    arg2, service2 = await ioc.call(func2, kwargs={"arg": 2})

    assert isinstance(service1, ServiceSingleton)
    assert arg1 == 1

    assert isinstance(service2, ServiceTransient)
    assert arg2 == 2


async def test_call_async_function_with_keyword_only_args(ioc: Container):
    async def func1(service: ServiceSingleton, *, arg: int):
        return service, arg

    async def func2(arg: int, *, service: ServiceTransient):
        return arg, service

    service1, arg1 = await ioc.call(func1, kwargs={"arg": 1})
    arg2, service2 = await ioc.call(func2, kwargs={"arg": 2})

    assert isinstance(service1, ServiceSingleton)
    assert arg1 == 1

    assert isinstance(service2, ServiceTransient)
    assert arg2 == 2


async def test_call_function_with_context(ioc: Container):
    def func(service: ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.store_dependent


async def test_call_async_function_with_context(ioc: Container):
    async def func(service: ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.store_dependent


async def test_call_callable_object(ioc: Container):
    class CallableClass:
        def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


async def test_call_async_callable_object(ioc: Container):
    class CallableClass:
        async def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


async def test_call_non_callable_object_should_fail(ioc: Container):
    class NonCallableClass:
        pass

    non_callable_object = NonCallableClass()

    with pytest.raises(CalledNonCallableError):
        await ioc.call(non_callable_object)
