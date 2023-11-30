from abc import ABC, abstractmethod
from http import HTTPStatus

from asgikit.responses import Response


class Template(ABC):
    @abstractmethod
    async def respond(
        self,
        response: Response,
        name: str,
        context: dict,
        status: HTTPStatus = HTTPStatus.OK,
    ):
        pass
