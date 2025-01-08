from typing import Any, NamedTuple


class RequestParam(NamedTuple):
    param_type: type
    param_meta: type | Any | None
    has_default: bool


class ServiceParam(NamedTuple):
    param_type: type
    service_name: str | None
    has_default: bool


class HandlerParams(NamedTuple):
    request: list[tuple[str, RequestParam]]
    service: list[tuple[str, ServiceParam]]
