from http import HTTPStatus

from selva.di.decorators import service
from selva.web import HttpResponse
from selva.web.response.into_response import IntoResponse


@service(provides=IntoResponse[int])
class IntIntoResponse:
    def into_response(self, value: int) -> HttpResponse:
        return HttpResponse(status=value)


@service(provides=IntoResponse[HTTPStatus])
class HTTPStatusIntoResponse:
    def into_response(self, value: HTTPStatus) -> HttpResponse:
        return HttpResponse(status=value)


@service(provides=IntoResponse[str])
class StrIntoResponse:
    def into_response(self, value: str) -> HttpResponse:
        return HttpResponse.text(value)


@service(provides=IntoResponse[list])
class ListIntoResponse:
    def into_response(self, value: list) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[dict])
class DictIntoResponse:
    def into_response(self, value: dict) -> HttpResponse:
        return HttpResponse.json(value)


@service(provides=IntoResponse[set])
class SetIntoResponse:
    def into_response(self, value: set) -> HttpResponse:
        return HttpResponse.json(value)
