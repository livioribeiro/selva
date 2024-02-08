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
        *,
        status: HTTPStatus = HTTPStatus.OK,
        content_type: str = None,
        stream: bool = False,
    ):
        raise NotImplementedError()

    @abstractmethod
    async def render(self, template_name: str, context: dict) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def render_str(self, source: str, context: dict) -> str:
        raise NotImplementedError()
