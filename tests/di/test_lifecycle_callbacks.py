import asyncio

from selva.di import Container, Scope
from selva.di.decorators import initializer, finalizer

from .fixtures import ioc


class Dependency:
    pass


class ServiceInitialize:
    def __init__(self):
        self.dependency = None

    @initializer
    def initialize(self, dependency: Dependency):
        self.dependency = dependency


class ServiceAsyncInitialize:
    def __init__(self):
        self.dependency = None

    @initializer
    async def initialize(self, dependency: Dependency):
        self.dependency = dependency


class Service:
    pass


class ServiceFinalize:
    @finalizer
    def finalize(self):
        print("finalize")


class ServiceAsyncFinalize:
    @finalizer
    async def finalize(self):
        print("async finalize", flush=True)


def run_finalizer(obj: Service):
    print("factory finalize", flush=True)


async def run_async_finalizer(obj: Service):
    print("factory async finalize", flush=True)


@finalizer(run_finalizer)
def factory_finalize() -> Service:
    return Service()


@finalizer(run_async_finalizer)
def factory_async_finalize() -> Service:
    return Service()


async def test_call_initialize(ioc: Container):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(ServiceInitialize, Scope.TRANSIENT)

    service = await ioc.get(ServiceInitialize)
    assert isinstance(service.dependency, Dependency)


async def test_call_async_initialize(ioc: Container):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(ServiceAsyncInitialize, Scope.TRANSIENT)

    service = await ioc.get(ServiceAsyncInitialize)
    assert isinstance(service.dependency, Dependency)


async def test_call_finalize(ioc: Container, capsys):
    ioc.register(ServiceFinalize, Scope.TRANSIENT)

    service = await ioc.get(ServiceFinalize)
    del service

    assert capsys.readouterr().out == "finalize\n"


async def test_call_async_finalize(ioc: Container, capsys):
    ioc.register(ServiceAsyncFinalize, Scope.TRANSIENT)

    service = await ioc.get(ServiceAsyncFinalize)
    del service

    await asyncio.sleep(0.1)  # gives the finalizer a chance to write to stdout
    assert capsys.readouterr().out == "async finalize\n"


async def test_call_factory_finalize(ioc: Container, capsys):
    ioc.register(factory_finalize, Scope.TRANSIENT)

    service = await ioc.get(Service)
    del service

    await asyncio.sleep(0.1)  # gives the finalizer a chance to write to stdout
    assert capsys.readouterr().out == "factory finalize\n"


async def test_call_factory_async_finalize(ioc: Container, capsys):
    ioc.register(factory_async_finalize, Scope.TRANSIENT)

    service = await ioc.get(Service)
    del service

    await asyncio.sleep(0.1)  # gives the finalizer a chance to write to stdout
    assert capsys.readouterr().out == "factory async finalize\n"
