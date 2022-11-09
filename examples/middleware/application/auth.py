from dataclasses import dataclass

from selva.di import service
from selva.web import RequestContext
from selva.web.errors import UnauthorizedError
from selva.web.request import FromRequest


@dataclass
class User:
    name: str


@service(provides=FromRequest[User])
class UserFromRequest:
    def from_request(self, context: RequestContext) -> User:
        if user := context.attributes.get("user"):
            return User(user)

        raise UnauthorizedError()
