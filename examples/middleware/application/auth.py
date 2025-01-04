from dataclasses import dataclass

from asgikit.requests import Request

from selva.web.converter.decorator import register_from_request
from selva.web.exception import HTTPUnauthorizedException


@dataclass
class User:
    name: str


@register_from_request(User)
class UserFromRequest:
    async def from_request(
        self,
        request: Request,
        original_type,
        parameter_name: str,
        metadata,
        optional: bool,
    ) -> User | None:
        if user := request.attributes.get("user"):
            return User(user)

        if optional:
            return None

        raise HTTPUnauthorizedException()
