from typing import Callable

from selva.web.context import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.converter.into_response import IntoResponse
from selva.web.converter.param_converter import RequestParamConverter

RequestBodyDecoder = Callable[[RequestContext], dict | list]
