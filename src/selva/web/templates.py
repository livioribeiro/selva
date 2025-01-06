from abc import ABC, abstractmethod

from asgikit.responses import Response


class Template(ABC):
    @abstractmethod
    async def respond(
        self,
        response: Response,
        template_name: str,
        context: dict,
        *,
        content_type: str = None,
        stream: bool = False,
    ):
        pass

    @abstractmethod
    async def render(self, template_name: str, context: dict) -> str:
        pass

    @abstractmethod
    async def render_str(self, source: str, context: dict) -> str:
        pass
