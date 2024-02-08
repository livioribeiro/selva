from collections.abc import Callable
from typing import Annotated, Literal, Type

from jinja2 import BaseLoader, BytecodeCache, Undefined
from pydantic import BaseModel, ConfigDict, Field

from selva._util.pydantic import DottedPath


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
    loader: Annotated[DottedPath[BaseLoader], Field(default=None)]
    cache_size: Annotated[int, Field(default=None)]
    auto_reload: Annotated[bool, Field(default=None)]
    bytecode_cache: Annotated[DottedPath[BytecodeCache], Field(default=None)]
