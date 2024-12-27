from dataclasses import dataclass

from asgikit.requests import Request

from selva.di import service
from selva.web.converter.from_request import FromRequest
from selva.web.exception import HTTPUnauthorizedException


@dataclass
class User:
    name: str


class UserFromRequest:
    def from_request(
        self, request: Request, original_type, parameter_name: str, metadata=None
    ) -> User:
        if user := request["user"]:
            return User(user)

        raise HTTPUnauthorizedException()


@service
def user_from_request() -> FromRequest[User]:
    return UserFromRequest()
