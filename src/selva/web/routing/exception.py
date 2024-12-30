class DuplicateRouteError(Exception):
    def __init__(self, route1: str, route2: str):
        super().__init__(f"path for {route1} clashes with {route2}")


class HandlerWithoutDecoratorError(Exception):
    def __init__(self, handler):
        super().__init__(
            f"{handler.__module__}.{handler.__qualname__}"
            " is not decorated with @handler"
        )
