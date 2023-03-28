from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_converter import RequestParamConverter


class MissingStrConverterImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{RequestParamConverter.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class MissingFromRequestImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{FromRequest.__name__}' found for type {param_type}"
        )
        self.param_type = param_type
