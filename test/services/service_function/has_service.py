from dependency_injector import transient


class Service:
    pass


@transient
async def service_factory() -> Service:
    return Service()
