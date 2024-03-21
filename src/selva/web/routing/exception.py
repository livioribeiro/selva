class DuplicateRouteError(Exception):
    def __init__(self, route1: str, route2: str):
        super().__init__(f"path for {route1} clashes with {route2}")


class ControllerWithoutDecoratorError(Exception):
    def __init__(self, controller: type):
        super().__init__(
            f"{controller.__module__}.{controller.__qualname__}"
            " is not decorated with @controller"
        )
