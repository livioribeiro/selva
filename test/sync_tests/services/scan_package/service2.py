from dependency_injector import singleton


class Service2:
    pass


@singleton
def service2_factory() -> Service2:
    return Service2()
