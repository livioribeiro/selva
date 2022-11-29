from dataclasses import dataclass

from selva.di import service
from selva.web.contexts import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.errors import HTTPUnauthorizedError


@dataclass
class User:
    name: str


@service(provides=FromRequest[User])
class UserFromRequest:
    def from_request(self, context: RequestContext) -> User:
        if user := context["user"]:
            return User(user)

        raise HTTPUnauthorizedError()
