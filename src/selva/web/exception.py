from http import HTTPStatus


class HTTPException(Exception):
    status_code: HTTPStatus

    def __init__(
        self,
        *,
        status_code: HTTPStatus | None = None,
        headers: dict[str, str] | None = None,
    ):
        if status_code:
            self.status_code = status_code

        self.headers = headers or {}


class WebSocketException(Exception):
    def __init__(self, status_code: int, reason: str = None) -> None:
        self.code = status_code
        self.reason = reason or ""


class HTTPBadRequestException(HTTPException):
    status_code = HTTPStatus.BAD_REQUEST


class HTTPNotFoundException(HTTPException):
    status_code = HTTPStatus.NOT_FOUND


class HTTPUnauthorizedException(HTTPException):
    status_code = HTTPStatus.UNAUTHORIZED


class HTTPForbiddenException(HTTPException):
    status_code = HTTPStatus.FORBIDDEN


class HTTPInternalServerException(HTTPException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
