from selva.di import Container

from .fixtures import ioc


class TestInterceptor:
    async def intercept(self, instance, service_type):
        setattr(instance, "intercepted", True)


class TestService:
    pass


async def test_intercept(ioc: Container):
    ioc.register(TestService)
    ioc.interceptor(TestInterceptor)

    instance = await ioc.get(TestService)

    assert getattr(instance, "intercepted")
