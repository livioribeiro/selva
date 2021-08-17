from dependency_injector import singleton


class Interface:
    pass


@singleton(provides=Interface)
class Implementation1(Interface):
    pass


@singleton(provides=Interface)
class Implementation2(Interface):
    pass
