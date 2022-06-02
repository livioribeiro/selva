from selva.di import service


class Service2:
    pass


@service
async def service2_factory() -> Service2:
    return Service2()
