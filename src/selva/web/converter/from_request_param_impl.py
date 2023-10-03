from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.from_request_param import FromRequestParam
from selva.web.error import HTTPBadRequestException


@service(provides=FromRequestParam[str])
class StrFromRequestParam:
    def from_param(self, value: str) -> str:
        return value

    def into_str(self, data: str) -> str:
        return data


@service(provides=FromRequestParam[int])
class IntFromRequestParam:
    def from_param(self, value: str) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@service(provides=FromRequestParam[float])
class FloatFromRequestParam:
    def from_param(self, value: str) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@service(provides=FromRequestParam[bool])
class BoolFromRequestParam:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    def from_param(self, value: str) -> bool:
        if value.lower() in BoolFromRequestParam.TRUE_VALUES:
            return True
        if value.lower() in BoolFromRequestParam.FALSE_VALUES:
            return False

        raise HTTPBadRequestException()

    def into_str(self, data: bool) -> str:
        return "true" if data else "false"


@service(provides=FromRequestParam[PurePath])
class PurePathFromRequestParam:
    def from_param(self, value: str) -> PurePath:
        return PurePath(value)

    def into_str(self, data: PurePath) -> str:
        return "/".join(data.parts)
