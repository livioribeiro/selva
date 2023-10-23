from selva.di import service


class Interface[T]:
    pass


@service(provides=Interface[int])
class Implementation(Interface[int]):
    pass
