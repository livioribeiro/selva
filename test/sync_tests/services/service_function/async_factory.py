from dependency_injector import singleton


class Service:
    pass


@singleton
async def service_factory() -> Service:
    return Service()
