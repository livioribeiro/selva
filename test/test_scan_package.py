import pytest

from dependency_injector.service import Scope

from . import ioc

pytestmark = pytest.mark.asyncio


async def test_scan_package(ioc):
    from .services import scan_package as module
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan(module)

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


async def test_scan_package_name(ioc):
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan("test.services.scan_package")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


async def test_scan_multiple_packages(ioc):
    from .services.scan_package import service1 as module
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan(module, "test.services.scan_package.service2")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


async def test_scan_generic_class(ioc):
    from .services.scan_package import generic as module

    ioc.scan(module)
    assert ioc.has(module.Interface[int])

    service = await ioc.get(module.Interface[int])
    assert isinstance(service, module.Implementation)


async def test_scan_scopes(ioc):
    from .services.scan_package import scopes as module

    ioc.scan(module)
    assert ioc.has(module.SingletonService, Scope.SINGLETON)
    assert ioc.has(module.DependentService, Scope.DEPENDENT)
    assert ioc.has(module.TransientService, Scope.TRANSIENT)
