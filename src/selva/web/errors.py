from http import HTTPStatus

from asgikit.errors.websocket import WebSocketDisconnectError, WebSocketStateError


class HttpError(Exception):
    def __init__(self, status: int | HTTPStatus):
        super().__init__()
        if status < 400:
            raise ValueError(
                f"HttpError status should be client or server error, {status} given"
            )
        self.status = status


class ClientError(HttpError):
    pass


class NotFoundError(ClientError):
    def __init__(self):
        super().__init__(HTTPStatus.NOT_FOUND)


class UnauthorizedError(ClientError):
    def __init__(self):
        super().__init__(HTTPStatus.UNAUTHORIZED)


class ForbidenError(ClientError):
    def __init__(self):
        super().__init__(HTTPStatus.FORBIDDEN)


class ServerError(HttpError):
    pass


class InternalServerError(ServerError):
    def __init__(self):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR)
