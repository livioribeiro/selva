from selva.web.converter.converter import Converter
from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_extractor import FromBody, ParamExtractor


class MissingFromRequestImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{FromRequest.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class MissingConverterImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{Converter.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class MissingRequestParamExtractorImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{ParamExtractor.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class PathParamNotFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f"path parameter '{name}' not found")
        self.name = name


class FromBodyOnWrongHttpMethodError(Exception):
    def __init__(self, param_name: str):
        super().__init__(
            f"'{param_name}' is annotated with {FromBody.__name__},"
            " but handler does not receive request body"
        )
