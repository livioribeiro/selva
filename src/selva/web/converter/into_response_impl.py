from http import HTTPStatus
from os import PathLike

from selva.di.decorator import service
from selva.web.converter.into_response import IntoResponse
from selva.web.response import FileResponse, JSONResponse, PlainTextResponse, Response


class IntIntoResponse(IntoResponse[int]):
    def into_response(self, value: int) -> Response:
        return Response(status_code=value)


class HTTPStatusIntoResponse(IntoResponse[HTTPStatus]):
    def into_response(self, value: HTTPStatus) -> Response:
        return Response(status_code=int(value))


class StrIntoResponse(IntoResponse[str]):
    def into_response(self, value: str) -> Response:
        return PlainTextResponse(value)


class ListIntoResponse(IntoResponse[list]):
    def into_response(self, value: list) -> Response:
        return JSONResponse(value)


class DictIntoResponse(IntoResponse[dict]):
    def into_response(self, value: dict) -> Response:
        return JSONResponse(value)


class SetIntoResponse(IntoResponse[set]):
    def into_response(self, value: set) -> Response:
        return JSONResponse(value)


class PathLikeIntoResponse(IntoResponse[PathLike]):
    def into_response(self, value: PathLike):
        return FileResponse(value)
