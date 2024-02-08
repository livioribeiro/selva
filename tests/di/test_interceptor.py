from typing import Any

from selva.di.container import Container


class TestInterceptor:
    async def intercept(self, instance: Any, _service_type: type):
        setattr(instance, "intercepted", True)


class TestService:
    pass


async def test_intercept(ioc: Container):
    ioc.register(TestService)
    ioc.interceptor(TestInterceptor)

    instance = await ioc.get(TestService)

    assert getattr(instance, "intercepted")
