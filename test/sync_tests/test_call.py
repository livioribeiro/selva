import pytest

from dependency_injector import Scope, SyncContainer
from dependency_injector.errors import CalledNonCallableError

from ..utils import Context


class ServiceSingleton:
    pass


class ServiceTransient:
    pass


class ServiceDependent:
    pass


@pytest.fixture
def ioc():
    container = SyncContainer()
    container.register(ServiceSingleton, Scope.SINGLETON)
    container.register(ServiceTransient, Scope.TRANSIENT)
    container.register(ServiceDependent, Scope.DEPENDENT)
    return container


def test_call_function(ioc):
    def func(service: ServiceSingleton):
        return service

    result = ioc.call(func)
    assert isinstance(result, ServiceSingleton)


def test_call_async_function(ioc):
    async def func(service: ServiceSingleton):
        return service

    result = ioc.call(func)
    assert isinstance(result, ServiceSingleton)


def test_call_function_multipe_services(ioc):
    def func(service1: ServiceSingleton, service2: ServiceTransient):
        return service1, service2

    service1, service2 = ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


def test_call_async_function_multipe_services(ioc):
    async def func(service1: ServiceSingleton, service2: ServiceTransient):
        return service1, service2

    service1, service2 = ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


def test_call_function_kwargs(ioc):
    def func(service1: ServiceSingleton, a):
        return service1, a

    service1, a = ioc.call(func, kwargs={"a": 1})
    assert isinstance(service1, ServiceSingleton)
    assert a == 1


def test_call_async_function_kwargs(ioc):
    async def func(service1: ServiceSingleton, a):
        return service1, a

    service1, a = ioc.call(func, kwargs={"a": 1})
    assert isinstance(service1, ServiceSingleton)
    assert a == 1


def test_call_function_args(ioc):
    def func(a, service1: ServiceSingleton):
        return a, service1

    a, service1 = ioc.call(func, args=[1])
    assert isinstance(service1, ServiceSingleton)
    assert a == 1


def test_call_async_function_args(ioc):
    async def func(a, service1: ServiceSingleton):
        return a, service1

    a, service1 = ioc.call(func, args=[1])
    assert isinstance(service1, ServiceSingleton)
    assert a == 1


def test_call_function_args_keyword_only(ioc):
    def func1(service1: ServiceSingleton, *, a: int):
        return service1, a

    def func2(a: int, *, service2: ServiceTransient):
        return a, service2

    result1, a1 = ioc.call(func1, kwargs={"a": 1})
    a2, result2 = ioc.call(func2, kwargs={"a": 2})

    assert isinstance(result1, ServiceSingleton)
    assert a1 == 1

    assert isinstance(result2, ServiceTransient)
    assert a2 == 2


def test_call_async_function_args_keyword_only(ioc):
    async def func1(service1: ServiceSingleton, *, a: int):
        return service1, a

    async def func2(a: int, *, service2: ServiceTransient):
        return a, service2

    result1, a1 = ioc.call(func1, kwargs={"a": 1})
    a2, result2 = ioc.call(func2, kwargs={"a": 2})

    assert isinstance(result1, ServiceSingleton)
    assert a1 == 1

    assert isinstance(result2, ServiceTransient)
    assert a2 == 2


def test_call_function_param_after_dependencies_should_fail(ioc):
    def func(a, service1: ServiceSingleton):
        pass

    with pytest.raises(Exception):
        ioc.call(func, [1])


def test_call_async_function_param_after_dependencies_should_fail(ioc):
    async def func(a, service1: ServiceSingleton):
        pass

    with pytest.raises(Exception):
        ioc.call(func, [1])


def test_call_function_with_context(ioc):
    def func(service: ServiceDependent):
        return service

    context = Context()

    result = ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.container.store_dependent


def test_call_async_function_with_context(ioc):
    async def func(service: ServiceDependent):
        return service

    context = Context()

    result = ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.container.store_dependent


def test_call_callable_object(ioc):
    class CallableClass:
        def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


def test_call_async_callable_object(ioc):
    class CallableClass:
        async def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


def test_call_non_callable_object_should_fail(ioc):
    class NonCallableClass:
        pass

    non_callable_object = NonCallableClass()

    with pytest.raises(CalledNonCallableError):
        ioc.call(non_callable_object)
