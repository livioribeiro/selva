from http import HTTPStatus

from starlette.exceptions import HTTPException, WebSocketException


class HTTPError(HTTPException):
    pass


class WebSocketError(WebSocketException):
    pass


class HTTPBadRequestError(HTTPError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.BAD_REQUEST, reason, headers)


class HTTPNotFoundError(HTTPError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.NOT_FOUND, reason, headers)


class HTTPUnauthorizedError(HTTPError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.UNAUTHORIZED, reason, headers)


class HTTPForbiddenError(HTTPError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.FORBIDDEN, reason, headers)


class HTTPInternalServerError(HTTPError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, reason, headers)
