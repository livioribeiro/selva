from dependency_injector import dependent


class Service:
    pass


@dependent
async def service_factory() -> Service:
    return Service()
