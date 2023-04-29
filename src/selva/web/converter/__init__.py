from typing import Callable

from selva.web.context import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.converter.from_request_param import FromRequestParam
from selva.web.converter.into_response import IntoResponse

RequestBodyDecoder = Callable[[RequestContext], dict | list]
