from dependency_injector import dependent, singleton, transient


@singleton
class Service1:
    pass


@transient
class Service2:
    pass


@dependent
class ServiceDependent:
    pass
