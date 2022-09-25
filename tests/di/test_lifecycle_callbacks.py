from selva.di import Container, initializer, finalizer

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


class FinalizerOrder1:
    @initializer
    def initialize(self):
        print("initialize 1", flush=True)

    @finalizer
    def finalize(self):
        print("finalize 1", flush=True)


class FinalizerOrder2:
    def __init__(self, dep: FinalizerOrder1):
        pass

    @initializer
    def initialize(self):
        print("initialize 2", flush=True)

    @finalizer
    def finalize(self):
        print("finalize 2", flush=True)


async def test_call_initialize(ioc: Container):
    ioc.register(Dependency)
    ioc.register(ServiceInitialize)

    service = await ioc.get(ServiceInitialize)
    assert isinstance(service.dependency, Dependency)


async def test_call_async_initialize(ioc: Container):
    ioc.register(Dependency)
    ioc.register(ServiceAsyncInitialize)

    service = await ioc.get(ServiceAsyncInitialize)
    assert isinstance(service.dependency, Dependency)


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
