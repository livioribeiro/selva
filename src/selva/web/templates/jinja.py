from collections.abc import Callable
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Literal, Type, TypeVar

from asgikit.responses import Response, respond_stream, respond_text
from jinja2 import (
    BaseLoader,
    BytecodeCache,
    Environment,
    FileSystemLoader,
    Undefined,
    select_autoescape,
)
from pydantic import BaseModel, ConfigDict, Field

from selva._util.pydantic import DottedPath
from selva.configuration import Settings
from selva.di import Inject, service
from selva.web.templates.template import Template

T = TypeVar("T")


class JinjaTemplateSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    block_start_string: Annotated[str, Field(default=None)]
    block_end_string: Annotated[str, Field(default=None)]
    variable_start_string: Annotated[str, Field(default=None)]
    variable_end_string: Annotated[str, Field(default=None)]
    comment_start_string: Annotated[str, Field(default=None)]
    comment_end_string: Annotated[str, Field(default=None)]
    line_statement_prefix: Annotated[str, Field(default=None)]
    line_comment_prefix: Annotated[str, Field(default=None)]
    trim_blocks: Annotated[bool, Field(default=None)]
    lstrip_blocks: Annotated[bool, Field(default=None)]
    newline_sequence: Annotated[Literal["\n", "\r\n", "\r"], Field(default=None)]
    keep_trailing_newline: Annotated[bool, Field(default=None)]
    extensions: Annotated[list[str], Field(default=None)]
    optimized: Annotated[bool, Field(default=None)]
    undefined: Annotated[DottedPath[Type[Undefined]], Field(default=None)]
    finalize: Annotated[DottedPath[Callable[..., None]], Field(default=None)]
    autoescape: Annotated[bool | DottedPath[Callable[[str], bool]], Field(default=None)]
    loader: Annotated[BaseLoader, Field(default=None)]
    cache_size: Annotated[int, Field(default=None)]
    auto_reload: Annotated[bool, Field(default=None)]
    bytecode_cache: Annotated[DottedPath[BytecodeCache], Field(default=None)]


@service(provides=Template)
class JinjaTemplate(Template):
    settings: Annotated[Settings, Inject]
    environment: Environment

    def initialize(self):
        jinja_settings = JinjaTemplateSettings.model_validate(
            self.settings.templates.jinja
        )

        kwargs = jinja_settings.model_dump(exclude_none=True)

        if "loader" not in kwargs:
            templates_path = Path(self.settings.templates.jinja.path).absolute()
            kwargs["loader"] = FileSystemLoader(templates_path)

        if "autoescape" not in kwargs:
            kwargs["autoescape"] = select_autoescape()

        self.environment = Environment(enable_async=True, **kwargs)

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
        if content_type:
            response.content_type = content_type
        elif not response.content_type:
            response.content_type = "text/html"

        template = self.environment.get_template(template_name)

        if stream:
            render_stream = template.generate_async(context)
            await respond_stream(response, render_stream, status=status)
        else:
            rendered = await template.render_async(context)
            await respond_text(response, rendered, status=status)

    async def render(self, template_name: str, context: dict) -> str:
        template = self.environment.get_template(template_name)
        return await template.render_async(context)

    async def render_str(self, source: str, context: dict) -> str:
        template = self.environment.from_string(source)
        return await template.render_async(context)
