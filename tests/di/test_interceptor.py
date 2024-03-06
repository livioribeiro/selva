from typing import Any

from selva.di.container import Container
from selva.di.decorator import service


@service
class MyInterceptor:
    async def intercept(self, instance: Any, _service_type: type):
        setattr(instance, "intercepted", True)


@service
class MyService:
    pass


async def test_intercept(ioc: Container):
    ioc.register(MyService)
    ioc.interceptor(MyInterceptor)

    instance = await ioc.get(MyService)

    assert getattr(instance, "intercepted")
