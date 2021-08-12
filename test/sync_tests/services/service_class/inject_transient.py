from dependency_injector import transient


@transient
class Service1:
    pass


@transient
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1
