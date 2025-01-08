from collections.abc import Callable
from typing import Annotated, Literal

from jinja2 import BaseLoader, BytecodeCache, Undefined, select_autoescape
from pydantic import BaseModel, ConfigDict, Field

from selva._util.pydantic import DottedPath


class JinjaTemplateSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paths: Annotated[list[str], Field(default_factory=lambda: ["resources/templates"])]
    block_start_string: str = None
    block_end_string: str = None
    variable_start_string: str = None
    variable_end_string: str = None
    comment_start_string: str = None
    comment_end_string: str = None
    line_statement_prefix: str = None
    line_comment_prefix: str = None
    trim_blocks: bool = None
    lstrip_blocks: bool = None
    newline_sequence: Literal["\n", "\r\n", "\r"] = None
    keep_trailing_newline: bool = None
    extensions: list[str] = None
    optimized: bool = None
    undefined: DottedPath[type[Undefined]] = None
    finalize: DottedPath[Callable[..., None]] = None
    autoescape: Annotated[
        bool | DottedPath[Callable[[str], bool]],
        Field(default_factory=select_autoescape),
    ]
    loader: DottedPath[BaseLoader] = None
    cache_size: int = None
    auto_reload: bool = None
    bytecode_cache: DottedPath[BytecodeCache] = None
