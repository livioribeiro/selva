from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.from_request_param import FromRequestParam
from selva.web.error import HTTPBadRequestError


@service(provides=FromRequestParam[str])
class StrFromRequestParam:
    def from_request_param(self, value: str) -> str:
        return value


@service(provides=FromRequestParam[int])
class IntFromRequestParam:
    def from_request_param(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise HTTPBadRequestError()


@service(provides=FromRequestParam[float])
class FloatFromRequestParam:
    def from_request_param(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise HTTPBadRequestError()


@service(provides=FromRequestParam[bool])
class BoolFromRequestParam:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    def from_request_param(self, value: str) -> bool | None:
        if value.lower() in BoolFromRequestParam.TRUE_VALUES:
            return True
        if value.lower() in BoolFromRequestParam.FALSE_VALUES:
            return False

        raise HTTPBadRequestError()


@service(provides=FromRequestParam[PurePath])
class PurePathFromRequestParam:
    def from_request_param(self, value: str) -> PurePath:
        return PurePath(value)
