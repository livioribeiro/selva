from dependency_injector import dependent, singleton


@dependent
class Service1:
    pass


@singleton
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1
