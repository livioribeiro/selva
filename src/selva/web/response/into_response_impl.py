from http import HTTPStatus

from selva.web import HttpResponse

from .into_response import IntoResponse


class IntIntoResponse(IntoResponse[int]):
    def into_response(self, value: int) -> HttpResponse:
        return HttpResponse(status=value)


class HTTPStatusIntoResponse(IntoResponse[HTTPStatus]):
    def into_response(self, value: HTTPStatus) -> HttpResponse:
        return HttpResponse(status=value)


class StrIntoResponse(IntoResponse[str]):
    def into_response(self, value: str) -> HttpResponse:
        return HttpResponse.text(value)


class ListIntoResponse(IntoResponse[list]):
    def into_response(self, value: list) -> HttpResponse:
        return HttpResponse.json(value)


class DictIntoResponse(IntoResponse[dict]):
    def into_response(self, value: dict) -> HttpResponse:
        return HttpResponse.json(value)


class SetIntoResponse(IntoResponse[set]):
    def into_response(self, value: set) -> HttpResponse:
        return HttpResponse.json(value)
