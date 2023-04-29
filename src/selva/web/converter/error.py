from selva.web.converter.from_request import FromRequest
from selva.web.converter.from_request_param import FromRequestParam
from selva.web.converter.param_extractor import RequestParamExtractor


class MissingFromRequestImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{FromRequest.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class MissingFromRequestParamImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{FromRequestParam.__name__}' found for type {param_type}"
        )
        self.param_type = param_type


class MissingRequestParamExtractorImplError(Exception):
    def __init__(self, param_type):
        super().__init__(
            f"no implementation of '{RequestParamExtractor.__name__}' found for type {param_type}"
        )
        self.param_type = param_type
