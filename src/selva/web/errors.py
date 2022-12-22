from http import HTTPStatus

from starlette.exceptions import HTTPException, WebSocketException


class HTTPClientError(HTTPException):
    pass


class HTTPNotFoundError(HTTPClientError):
    def __init__(self):
        super().__init__(HTTPStatus.NOT_FOUND)


class HTTPUnauthorizedError(HTTPClientError):
    def __init__(self):
        super().__init__(HTTPStatus.UNAUTHORIZED)


class HTTPForbiddenError(HTTPClientError):
    def __init__(self):
        super().__init__(HTTPStatus.FORBIDDEN)


class HTTPServerError(HTTPException):
    pass


class HTTPInternalServerError(HTTPServerError):
    def __init__(self):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR)
