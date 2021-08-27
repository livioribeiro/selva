from dependency_injector import dependent, singleton, transient


@singleton
class SingletonService:
    pass


@dependent
class DependentService:
    pass


@transient
class TransientService:
    pass
