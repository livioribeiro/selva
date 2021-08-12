from dependency_injector import transient


class Service1:
    pass


@transient
async def service1_factory() -> Service1:
    return Service1()


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@transient
async def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)
