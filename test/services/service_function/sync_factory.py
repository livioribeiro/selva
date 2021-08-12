from dependency_injector import singleton


class Service:
    pass


@singleton
def service_factory() -> Service:
    return Service()
