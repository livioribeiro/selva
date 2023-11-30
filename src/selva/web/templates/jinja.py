import typing
from collections.abc import Callable
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Any, Generic, Literal, Type, TypeVar

from asgikit.responses import Response, respond_text
from jinja2 import (
    BaseLoader,
    BytecodeCache,
    Environment,
    FileSystemLoader,
    Undefined,
    select_autoescape,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    ValidatorFunctionWrapHandler,
)
from pydantic_core import PydanticCustomError, core_schema

from selva._util.import_item import import_item
from selva.configuration import Settings
from selva.di import Inject, service
from selva.web.templates.template import Template

T = TypeVar("T")


class DottedPath(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        origin = typing.get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            item_tp = Any
        else:
            item_tp = typing.get_args(source_type)[0]

        item_schema = handler.generate_schema(item_tp)

        def validate_from_str(
            value: str, handler: ValidatorFunctionWrapHandler
        ) -> DottedPath[item_tp]:
            try:
                item = import_item(value)
            except ImportError as e:
                raise PydanticCustomError("invalid_dotted_path", str(e))

            return handler(item)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_wrap_validator_function(
                    validate_from_str, item_schema
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_subclass_schema(str),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: f"{instance.__module__}.{instance.__qualname__}",
                when_used="unless-none",
            ),
        )


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
        status: HTTPStatus = HTTPStatus.OK,
    ):
        response.content_type = "text/html"
        template = self.environment.get_template(template_name)
        rendered = await template.render_async(context)
        await respond_text(response, rendered, status=status)
