import pytest

from dependency_injector import transient

from . import ioc
from .services import call as module

pytestmark = pytest.mark.asyncio


async def test_call_function(ioc):
    ioc.scan_packages(module)

    def caller(service1: module.Service):
        pass

    await ioc.call(caller)


async def test_call_function_args(ioc):
    ioc.scan_packages(module)

    def caller(service1: module.Service, a: int):
        pass

    await ioc.call(caller, kwargs={"a": 1})


async def test_call_async_function(ioc):
    ioc.scan_packages(module)

    async def caller(service1: module.Service):
        pass

    await ioc.call(caller)
