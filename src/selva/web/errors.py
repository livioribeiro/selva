from http import HTTPStatus


class HttpError(Exception):
    def __init__(self, status: HTTPStatus):
        self.status = status


class ClientError(HttpError):
    pass


class NotFoundError(ClientError):
    def __init__(self):
        super().__init__(HTTPStatus.NOT_FOUND)


class ServerError(HttpError):
    pass


class InternalServerError(ServerError):
    def __init__(self):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR)
