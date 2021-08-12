from dependency_injector import singleton


class Interface:
    def method(self):
        pass


class Implementation(Interface):
    def method(self):
        pass


@singleton(provides=Interface)
async def factory() -> Interface:
    return Implementation()
