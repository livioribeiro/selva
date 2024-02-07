from collections.abc import Callable
from types import ModuleType
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import URL, make_url

from selva._util.pydantic import DottedPath


class SqlAlchemyExecutionOptions(BaseModel):
    """SQLAlchemy execution options.

    Defined in https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.execution_options
    """

    logging_token: Annotated[str, Field(default=None)]
    isolation_level: Annotated[str, Field(default=None)]
    no_parameters: Annotated[bool, Field(default=None)]
    stream_results: Annotated[bool, Field(default=None)]
    max_row_buffer: Annotated[int, Field(default=None)]
    yield_per: Annotated[int, Field(default=None)]
    insertmanyvalues_page_size: Annotated[int, Field(default=None)]
    schema_translate_map: Annotated[dict[str | None, str], Field(default=None)]


class SqlAlchemyOptions(BaseModel):
    """SQLAlchemy options

    Defined in https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
    """

    connect_args: Annotated[dict[str, Any], Field(default=None)]
    echo: Annotated[bool, Field(default=None)]
    echo_pool: Annotated[bool, Field(default=None)]
    enable_from_linting: Annotated[bool, Field(default=None)]
    execution_options: Annotated[SqlAlchemyExecutionOptions, Field(default=None)]
    hide_parameters: Annotated[bool, Field(default=None)]
    insertmanyvalues_page_size: Annotated[int, Field(default=None)]
    isolation_level: Annotated[str, Field(default=None)]
    json_deserializer: Annotated[DottedPath[Callable], Field(default=None)]
    json_serializer: Annotated[DottedPath[Callable], Field(default=None)]
    label_length: Annotated[int, Field(default=None)]
    logging_name: Annotated[str, Field(default=None)]
    max_identifier_length: Annotated[int, Field(default=None)]
    max_overflow: Annotated[int, Field(default=None)]
    module: Annotated[DottedPath[ModuleType], Field(default=None)]
    paramstyle: Annotated[
        Literal["qmark", "numeric", "named", "format", "pyformat"], Field(default=None)
    ]
    poolclass: Annotated[DottedPath, Field(default=None)]
    pool_logging_name: Annotated[str, Field(default=None)]
    pool_pre_ping: Annotated[bool, Field(default=None)]
    pool_size: Annotated[int, Field(default=None)]
    pool_recycle: Annotated[int, Field(default=None)]
    pool_reset_on_return: Annotated[Literal["rollback", "commit"], Field(default=None)]
    pool_timeout: Annotated[int, Field(default=None)]
    pool_use_lifo: Annotated[bool, Field(default=None)]
    plugins: Annotated[list[str], Field(default=None)]
    query_cache_size: Annotated[int, Field(default=None)]
    use_insertmanyvalues: Annotated[bool, Field(default=None)]


class SqlAlchemySettings(BaseModel):
    """Settings for a SQLAlchemy connection defined in a settings file."""

    url: Annotated[str, Field(default=None)]
    username: Annotated[str, Field(default=None)]
    password: Annotated[str, Field(default=None)]
    drivername: Annotated[str, Field(default=None)]
    host: Annotated[str, Field(default=None)]
    port: Annotated[int, Field(default=None)]
    database: Annotated[str, Field(default=None)]
    query: Annotated[dict[str, str], Field(default=None)]
    options: Annotated[SqlAlchemyOptions, Field(default=None)]

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.url and (self.drivername or self.host or self.port or self.database):
            raise ValueError(
                "Either 'url' should be provided, or 'drivername', 'host', 'port' and 'database'"
            )

        return self

    def get_url(self) -> URL:
        if url := self.url:
            url = make_url(url)
            if username := self.username:
                url = url.set(username=username)
            if password := self.password:
                url = url.set(password=password)
            if query := self.query:
                url = url.set(query=query)
        else:
            url = URL.create(
                drivername=self.drivername,
                host=self.host,
                port=self.port,
                database=self.database,
                username=self.username,
                password=self.password,
                query=self.query,
            )

        return url
