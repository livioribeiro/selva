from . import ioc
from .services import call as module


def test_call_function(ioc):
    ioc.scan_packages(module)

    def caller(service1: module.Service):
        pass

    ioc.call(caller)


def test_call_function_args(ioc):
    ioc.scan_packages(module)

    def caller(service1: module.Service, a: int):
        pass

    ioc.call(caller, kwargs={"a": 1})
