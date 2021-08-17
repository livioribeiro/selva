from dependency_injector import singleton


class Service:
    pass


@singleton
def service_factory1() -> Service:
    return Service()


@singleton
def service_factory2() -> Service:
    return Service()
