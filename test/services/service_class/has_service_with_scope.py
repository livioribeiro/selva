from dependency_injector import dependent, singleton, transient


@transient
class ServiceTransient:
    pass


@dependent
class ServiceDependent:
    pass


@singleton
class ServiceSingleton:
    pass
