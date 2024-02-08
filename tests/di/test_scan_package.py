from selva.di.container import Container


async def test_scan_package_by_module(ioc: Container):
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


async def test_scan_package_by_name(ioc: Container):
    from .services.scan_package.service_class import Service1
    from .services.scan_package.service_function import Service2

    ioc.scan("tests.di.services.scan_package")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


async def test_scan_multiple_packages(ioc: Container):
    from .services.scan_package import service_class as module
    from .services.scan_package.service_class import Service1
    from .services.scan_package.service_function import Service2

    ioc.scan(module, "tests.di.services.scan_package.service_function")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


async def test_scan_generic_class(ioc: Container):
    from .services.scan_package import generic as module

    ioc.scan(module)
    assert ioc.has(module.Interface[int])

    service = await ioc.get(module.Interface[int])
    assert isinstance(service, module.Implementation)
