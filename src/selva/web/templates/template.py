from abc import ABC, abstractmethod
from http import HTTPStatus

from asgikit.responses import Response


class Template(ABC):
    @abstractmethod
    async def respond(
        self,
        response: Response,
        template_name: str,
        context: dict,
        status: HTTPStatus = HTTPStatus.OK,
    ):
        pass
