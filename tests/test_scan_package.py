from ward import test

from dependency_injector import Container, Scope

from .fixtures import ioc


@test("scan package by module")
async def _(ioc: Container = ioc):
    from .services import scan_package as module
    from .services.scan_package.service_class import Service1
    from .services.scan_package.service_function import Service2

    ioc.scan(module)

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


@test("scan package by name")
async def _(ioc: Container = ioc):
    from .services.scan_package.service_class import Service1
    from .services.scan_package.service_function import Service2

    ioc.scan("tests.services.scan_package")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


@test("scan multiple packages")
async def _(ioc: Container = ioc):
    from .services.scan_package import service_class as module
    from .services.scan_package.service_class import Service1
    from .services.scan_package.service_function import Service2

    ioc.scan(module, "tests.services.scan_package.service_function")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


@test("scan generic class")
async def _(ioc: Container = ioc):
    from .services.scan_package import generic as module

    ioc.scan(module)
    assert ioc.has(module.Interface[int])

    service = await ioc.get(module.Interface[int])
    assert isinstance(service, module.Implementation)


@test("scan scopes")
async def _(ioc: Container = ioc):
    from .services.scan_package import scopes as module

    ioc.scan(module)
    assert ioc.has(module.SingletonService, Scope.SINGLETON)
    assert ioc.has(module.DependentService, Scope.DEPENDENT)
    assert ioc.has(module.TransientService, Scope.TRANSIENT)


@test("scan dataclass")
async def _(ioc: Container = ioc):
    from .services.scan_package import service_dataclass as module

    ioc.scan(module)

    service = await ioc.get(module.ServiceDataclass)
    assert isinstance(service.dependency, module.Dependency)
