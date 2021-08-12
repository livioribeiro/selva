from dependency_injector import dependent


@dependent
class Service1:
    pass


@dependent
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1
