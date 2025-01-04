from asgikit.requests import Request


class DuplicateRouteError(Exception):
    def __init__(self, route1: str, route2: str):
        super().__init__(f"path for {route1} clashes with {route2}")


class HandlerWithoutDecoratorError(Exception):
    def __init__(self, handler):
        super().__init__(
            f"{handler.__module__}.{handler.__qualname__}"
            " is not decorated with @handler"
        )


class HandlerNotAsyncError(Exception):
    def __init__(self, handler):
        super().__init__(f"{handler.__module__}.{handler.__qualname__} must be async")


class HandlerMissingRequestArgumentError(Exception):
    def __init__(self, handler):
        super().__init__(
            f"{handler.__module__}.{handler.__qualname__}"
            " must receive at least the 'request' parameter"
        )


class HandlerRequestTypeError(Exception):
    def __init__(self, handler):
        super().__init__(
            f"{handler.__module__}.{handler.__qualname__}"
            " first parameter annotation must be "
            f"'{Request.__module__}.{Request.__name__}'"
        )


class HandlerUntypedParametersError(Exception):
    def __init__(self, handler, params: list[str]):
        param_list = ", ".join(params)
        super().__init__(
            f"{handler.__module__}.{handler.__qualname__}"
            " parameters must be typed:"
            f" ({param_list})"
        )
