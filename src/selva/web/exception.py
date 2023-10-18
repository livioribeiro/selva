from http import HTTPStatus


class HTTPException(Exception):
    status: HTTPStatus

    def __init__(
        self,
        *,
        status: HTTPStatus = None,
        headers: dict[str, str] = None,
    ):
        if status:
            self.status = status

        self.headers = headers or {}


class WebSocketException(Exception):
    def __init__(self, code: int, reason: str = None) -> None:
        self.code = code
        self.reason = reason or ""


class HTTPBadRequestException(HTTPException):
    status = HTTPStatus.BAD_REQUEST


class HTTPNotFoundException(HTTPException):
    status = HTTPStatus.NOT_FOUND


class HTTPUnauthorizedException(HTTPException):
    status = HTTPStatus.UNAUTHORIZED


class HTTPForbiddenException(HTTPException):
    status = HTTPStatus.FORBIDDEN


class HTTPInternalServerException(HTTPException):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
