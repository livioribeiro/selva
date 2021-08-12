from dependency_injector import transient


@transient
class Service1:
    def __init__(self, service2: "Service2"):
        pass


@transient
class Service2:
    def __init__(self, service1: Service1):
        pass
