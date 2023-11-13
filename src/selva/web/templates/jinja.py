import copy
from collections.abc import Callable, MutableMapping
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Any, Literal, Type

from asgikit.responses import Response, respond_text
from jinja2 import (
    BaseLoader,
    Environment,
    FileSystemLoader,
    Undefined,
    select_autoescape,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator

from selva._util.import_item import import_item
from selva.configuration import Settings
from selva.di import Inject, service
from selva.web.templates.template import Template


class MyUndefined(Undefined):
    pass


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
    undefined: Annotated[Type[Undefined], Field(default=None)]
    finalize: Annotated[Callable[..., None], Field(default=None)]
    autoescape: Annotated[bool | Callable[[str], bool], Field(default=None)]
    loader: Annotated[BaseLoader, Field(default=None)]
    cache_size: Annotated[int, Field(default=None)]
    auto_reload: Annotated[bool, Field(default=None)]
    bytecode_cache: Annotated[object, Field(default=None)]

    @model_validator(mode="before")
    @classmethod
    def model_validator(cls, data: Any):
        if isinstance(data, MutableMapping):
            if undefined := data.get("undefined"):
                if not isinstance(undefined, str):
                    raise TypeError(
                        "Jinja setting 'undefined' must be a python dotted path"
                    )

                data["undefined"] = import_item(undefined)

            if finalize := data.get("finalize"):
                if not isinstance(finalize, str):
                    raise TypeError(
                        "Jinja setting 'finalize' must be a python dotted path"
                    )

                data["finalize"] = import_item(finalize)

            if autoescape := data.get("autoescape"):
                match autoescape:
                    case value if isinstance(value, bool):
                        autoescape = value
                    case "true" | "True":
                        autoescape = True
                    case "false" | "False":
                        autoescape = False
                    case value if isinstance(value, str):
                        autoescape = import_item(value)
                    case _:
                        raise TypeError(
                            "Jinja setting 'autoescape' must be bool or str"
                        )

                data["autoescape"] = autoescape

        return data


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
        status: HTTPStatus = HTTPStatus.OK,
    ):
        response.content_type = "text/html"
        template = self.environment.get_template(template_name)
        rendered = await template.render_async(context)
        await respond_text(response, rendered, status=status)
