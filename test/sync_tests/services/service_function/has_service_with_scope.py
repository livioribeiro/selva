from dependency_injector import dependent, singleton, transient


class ServiceTransient:
    pass


@transient
async def service_transient_factory() -> ServiceTransient:
    return ServiceTransient


class ServiceDependent:
    pass


@dependent
async def service_dependent_factory() -> ServiceDependent:
    return ServiceDependent


class ServiceSingleton:
    pass


@singleton
async def service_singleton_factory() -> ServiceSingleton:
    return ServiceSingleton
