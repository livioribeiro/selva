from typing import Annotated

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.inject import Inject


@service
class Dependency:
    pass


@service
class ServiceInitialize:
    initialized = False

    def initialize(self):
        self.initialized = True


@service
class ServiceAsyncInitialize:
    initialized = False

    async def initialize(self):
        self.initialized = True


@service
class Service:
    pass


@service
class ServiceFinalize:
    def finalize(self):
        print("finalize")


@service
class ServiceAsyncFinalize:
    async def finalize(self):
        print("async finalize", flush=True)


@service
def factory_finalize() -> Service:
    yield Service()
    print("factory finalize", flush=True)


@service
async def factory_async_finalize() -> Service:
    yield Service()
    print("factory async finalize", flush=True)


@service
class FinalizerOrder1:
    def initialize(self):
        print("initialize 1", flush=True)

    def finalize(self):
        print("finalize 1", flush=True)


@service
class FinalizerOrder2:
    dep: Annotated[FinalizerOrder1, Inject]

    def initialize(self):
        print("initialize 2", flush=True)

    def finalize(self):
        print("finalize 2", flush=True)


async def test_call_initialize(ioc: Container):
    ioc.register(ServiceInitialize)

    instance = await ioc.get(ServiceInitialize)
    assert instance.initialized


async def test_call_async_initialize(ioc: Container):
    ioc.register(Dependency)
    ioc.register(ServiceAsyncInitialize)

    instance = await ioc.get(ServiceAsyncInitialize)
    assert instance.initialized


async def test_call_finalize(ioc: Container, capsys):
    ioc.register(ServiceFinalize)

    await ioc.get(ServiceFinalize)
    await ioc.run_finalizers()

    assert capsys.readouterr().out == "finalize\n"


async def test_call_async_finalize(ioc: Container, capsys):
    ioc.register(ServiceAsyncFinalize)

    await ioc.get(ServiceAsyncFinalize)
    await ioc.run_finalizers()

    assert capsys.readouterr().out == "async finalize\n"


async def test_call_factory_finalize(ioc: Container, capsys):
    ioc.register(factory_finalize)

    await ioc.get(Service)
    await ioc.run_finalizers()

    assert capsys.readouterr().out == "factory finalize\n"


async def test_call_factory_async_finalize(ioc: Container, capsys):
    ioc.register(factory_async_finalize)

    await ioc.get(Service)
    await ioc.run_finalizers()

    assert capsys.readouterr().out == "factory async finalize\n"


async def test_finalizer_order(ioc: Container, capsys):
    ioc.register(FinalizerOrder1)
    ioc.register(FinalizerOrder2)

    await ioc.get(FinalizerOrder2)
    await ioc.run_finalizers()

    expected = "initialize 1\ninitialize 2\nfinalize 2\nfinalize 1\n"
    assert capsys.readouterr().out == expected
