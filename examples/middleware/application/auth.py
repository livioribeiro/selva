from dataclasses import dataclass

from asgikit.requests import Request
from asgikit.responses import Response

from selva.di import service
from selva.web.converter.from_request import FromRequest
from selva.web.error import HTTPUnauthorizedException


@dataclass
class User:
    name: str


@service(provides=FromRequest[User])
class UserFromRequest:
    def from_request(self, request: Request, response: Response) -> User:
        if user := request["user"]:
            return User(user)

        raise HTTPUnauthorizedException()
