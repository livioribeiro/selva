from http import HTTPStatus
from os import PathLike

from selva.di.decorators import service
from selva.web.converter.into_response import IntoResponse
from selva.web.responses import FileResponse, JSONResponse, PlainTextResponse, Response


@service(provides=IntoResponse[int])
class IntIntoResponse:
    def into_response(self, value: int) -> Response:
        return Response(status_code=value)


@service(provides=IntoResponse[HTTPStatus])
class HTTPStatusIntoResponse:
    def into_response(self, value: HTTPStatus) -> Response:
        return Response(status_code=int(value))


@service(provides=IntoResponse[str])
class StrIntoResponse:
    def into_response(self, value: str) -> Response:
        return PlainTextResponse(value)


@service(provides=IntoResponse[list])
class ListIntoResponse:
    def into_response(self, value: list) -> Response:
        return JSONResponse(value)


@service(provides=IntoResponse[dict])
class DictIntoResponse:
    def into_response(self, value: dict) -> Response:
        return JSONResponse(value)


@service(provides=IntoResponse[set])
class SetIntoResponse:
    def into_response(self, value: set) -> Response:
        return JSONResponse(value)


@service(provides=IntoResponse[PathLike])
class PathLikeIntoResponse:
    def into_response(self, value: PathLike):
        return FileResponse(value)
