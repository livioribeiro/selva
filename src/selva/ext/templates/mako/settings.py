from collections.abc import Callable
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from selva._util.pydantic import DottedPath


class MakoTemplateSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directories: Annotated[
        list[str], Field(default_factory=lambda: ["resources/templates"])
    ]
    module_directory: str = None
    filesystem_checks: bool = False
    collection_size: int = None
    format_exceptions: bool = None
    error_handler: DottedPath = None
    encoding_errors: Literal[
        "strict", "ignore", "replace", "xmlcharrefreplace", "htmlentityreplace"
    ] = None
    cache_enabled: bool = None
    cache_impl: str = None
    cache_args: DottedPath[dict] = None
    modulename_callable: DottedPath[Callable] = None
    module_writer: DottedPath[Callable] = None
    default_filters: list[str] = None
    buffer_filters: list[str] = None
    strict_undefined: bool = None
    imports: list[str] = None
    future_imports: list[str] = None
    enable_loop: bool = None
    input_encoding: str = "utf-8"
    preprocessor: DottedPath[Callable] = None
    lexer_cls: DottedPath[type] = None
    include_error_handler: DottedPath[Callable] = None
