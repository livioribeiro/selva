from http import HTTPStatus

from asgikit.responses import HttpResponse

from selva.di import service

from .into_response import IntoResponse


@service(provides=IntoResponse[int])
class IntIntoResponse(IntoResponse[int]):
    def into_response(self, value: int) -> HttpResponse:
        return HttpResponse(status=value)


@service(provides=IntoResponse[HTTPStatus])
class HTTPStatusIntoResponse(IntoResponse[HTTPStatus]):
    def into_response(self, value: HTTPStatus) -> HttpResponse:
        return HttpResponse(status=value)


@service(provides=IntoResponse[str])
class StrIntoResponse(IntoResponse[str]):
    def into_response(self, value: str) -> HttpResponse:
        return HttpResponse.text(value)


@service(provides=IntoResponse[list])
class ListIntoResponse(IntoResponse[list]):
    def into_response(self, value: list) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[dict])
class DictIntoResponse(IntoResponse[dict]):
    def into_response(self, value: dict) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[set])
class SetIntoResponse(IntoResponse[set]):
    def into_response(self, value: set) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[tuple])
class TupleIntoResponse(IntoResponse[tuple]):
    def into_response(self, value: tuple) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[None])
class NoneIntoResponse(IntoResponse[None]):
    def into_response(self, value: None) -> HttpResponse:
        return HttpResponse.no_content()
