from http import HTTPStatus

from starlette.exceptions import HTTPException, WebSocketException


class HTTPClientError(HTTPException):
    def __init__(
        self,
        status_code: HTTPStatus,
        reason: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        if not (400 <= status_code < 500):
            raise ValueError(
                f"{self.__class__.__name__} status_code should be in '400' range"
            )

        super().__init__(status_code, reason, headers)


class HTTPBadRequestError(HTTPClientError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.BAD_REQUEST, reason, headers)


class HTTPNotFoundError(HTTPClientError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.NOT_FOUND, reason, headers)


class HTTPUnauthorizedError(HTTPClientError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.UNAUTHORIZED, reason, headers)


class HTTPForbiddenError(HTTPClientError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.FORBIDDEN, reason, headers)


class HTTPServerError(HTTPException):
    def __init__(
        self,
        status_code: HTTPStatus,
        reason: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        if not (500 <= status_code < 600):
            raise ValueError(
                f"{self.__class__.__name__} status_code should be in '500' range"
            )

        super().__init__(status_code, reason, headers)


class HTTPInternalServerError(HTTPServerError):
    def __init__(
        self, reason: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, reason, headers)
