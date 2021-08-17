from . import ioc


def test_scan_package(ioc):
    from .services import scan_package as module
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan(module)

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = ioc.get(Service1)
    service2 = ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


def test_scan_package_name(ioc):
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan("test.sync_tests.services.scan_package")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = ioc.get(Service1)
    service2 = ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)


def test_scan_multiple_packages(ioc):
    from .services.scan_package import service1
    from .services.scan_package.service1 import Service1
    from .services.scan_package.service2 import Service2

    ioc.scan(service1, "test.sync_tests.services.scan_package.service2")

    assert ioc.has(Service1)
    assert ioc.has(Service2)

    service1 = ioc.get(Service1)
    service2 = ioc.get(Service2)

    assert isinstance(service1, Service1)
    assert isinstance(service2, Service2)
