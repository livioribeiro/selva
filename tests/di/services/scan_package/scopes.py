from selva.di import Scope, service


@service
class SingletonService:
    pass


@service(scope=Scope.DEPENDENT)
class DependentService:
    pass


@service(scope=Scope.TRANSIENT)
class TransientService:
    pass
