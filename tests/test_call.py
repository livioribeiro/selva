from ward import fixture, raises, test

from dependency_injector import Container, Scope
from dependency_injector.errors import CalledNonCallableError

from .utils import Context


class ServiceSingleton:
    pass


class ServiceTransient:
    pass


class ServiceDependent:
    pass


@fixture
async def ioc():
    container = Container()
    container.register(ServiceSingleton, Scope.SINGLETON)
    container.register(ServiceTransient, Scope.TRANSIENT)
    container.register(ServiceDependent, Scope.DEPENDENT)
    return container


@test("call function")
async def _(ioc=ioc):
    def func(service: ServiceSingleton):
        return service

    result = await ioc.call(func)
    assert isinstance(result, ServiceSingleton)


@test("call async function")
async def _(ioc=ioc):
    async def func(service: ServiceSingleton):
        return service

    result = await ioc.call(func)
    assert isinstance(result, ServiceSingleton)


@test("call function with multiple dependencies")
async def _(ioc=ioc):
    def func(service1: ServiceSingleton, service2: ServiceTransient):
        return service1, service2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


@test("call async function with multipe dependencies")
async def _(ioc=ioc):
    async def func(service1: ServiceSingleton, service2: ServiceTransient):
        return service1, service2

    service1, service2 = await ioc.call(func)
    assert isinstance(service1, ServiceSingleton)
    assert isinstance(service2, ServiceTransient)


@test("call function with kwargs")
async def _(ioc=ioc):
    def func(service: ServiceSingleton, arg):
        return service, arg

    service, arg = await ioc.call(func, kwargs={"arg": 1})
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


@test("call async function with kwargs")
async def _(ioc=ioc):
    async def func(service: ServiceSingleton, arg):
        return service, arg

    service, arg = await ioc.call(func, kwargs={"arg": 1})
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


@test("call function with args")
async def _(ioc=ioc):
    def func(arg, service: ServiceSingleton):
        return arg, service

    arg, service = await ioc.call(func, args=[1])
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


@test("call async function with args")
async def _(ioc=ioc):
    async def func(arg, service: ServiceSingleton):
        return arg, service

    arg, service = await ioc.call(func, args=[1])
    assert isinstance(service, ServiceSingleton)
    assert arg == 1


@test("call function with keyword only args")
async def _(ioc=ioc):
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


@test("call async function with keyword only args")
async def _(ioc=ioc):
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


@test("call function with context")
async def _(ioc=ioc):
    def func(service: ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.store_dependent


@test("call async function with context")
async def _(ioc=ioc):
    async def func(service: ServiceDependent):
        return service

    context = Context()

    result = await ioc.call(func, context=context)
    assert isinstance(result, ServiceDependent)
    assert id(context) in ioc.store_dependent


@test("call callable object")
async def _(ioc=ioc):
    class CallableClass:
        def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


@test("call async callable object")
async def _(ioc=ioc):
    class CallableClass:
        async def __call__(self, service: ServiceSingleton):
            return service

    callable_object = CallableClass()

    result = await ioc.call(callable_object)
    assert isinstance(result, ServiceSingleton)


@test("call non callable object should fail")
async def _(ioc=ioc):
    class NonCallableClass:
        pass

    non_callable_object = NonCallableClass()

    with raises(CalledNonCallableError):
        await ioc.call(non_callable_object)
