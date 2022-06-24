from typing import Protocol, runtime_checkable


@runtime_checkable
class Interceptor(Protocol):
    async def intercept(self, instance: object, service_type: type):
        raise NotImplementedError()
