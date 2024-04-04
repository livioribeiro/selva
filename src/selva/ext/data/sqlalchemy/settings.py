from collections.abc import Callable
from types import ModuleType
from typing import Any, Literal, Self, Type

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import JoinTransactionMode

from selva._util.pydantic import DottedPath


class SqlAlchemyExecutionOptions(BaseModel):
    """SQLAlchemy execution options.

    Defined in https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.execution_options
    """

    model_config = ConfigDict(extra="forbid")

    logging_token: str = None
    isolation_level: str = None
    no_parameters: bool = None
    stream_results: bool = None
    max_row_buffer: int = None
    yield_per: int = None
    insertmanyvalues_page_size: int = None
    schema_translate_map: dict[str | None, str] = None


class SqlAlchemyOptions(BaseModel):
    """SQLAlchemy options

    Defined in https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
    """

    model_config = ConfigDict(extra="forbid")

    connect_args: dict[str, Any] = None
    echo: bool = None
    echo_pool: bool = None
    enable_from_linting: bool = None
    execution_options: SqlAlchemyExecutionOptions = None
    hide_parameters: bool = None
    insertmanyvalues_page_size: int = None
    isolation_level: str = None
    json_deserializer: DottedPath[Callable] = None
    json_serializer: DottedPath[Callable] = None
    label_length: int = None
    logging_name: str = None
    max_identifier_length: int = None
    max_overflow: int = None
    module: DottedPath[ModuleType] = None
    paramstyle: Literal["qmark", "numeric", "named", "format", "pyformat"] = None
    poolclass: DottedPath = None
    pool_logging_name: str = None
    pool_pre_ping: bool = None
    pool_size: int = None
    pool_recycle: int = None
    pool_reset_on_return: Literal["rollback", "commit"] = None
    pool_timeout: int = None
    pool_use_lifo: bool = None
    plugins: list[str] = None
    query_cache_size: int = None
    use_insertmanyvalues: bool = None


class SqlAlchemyEngineSettings(BaseModel):
    """Settings for a SQLAlchemy connection defined in a settings file."""

    model_config = ConfigDict(extra="forbid")

    url: str = None
    username: str = None
    password: str = None
    drivername: str = None
    host: str = None
    port: int = None
    database: str = None
    query: dict[str, str] = None
    options: SqlAlchemyOptions = None

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


class SqlAlchemySessionOptions(BaseModel):
    class_: DottedPath[Type[AsyncSession]] = Field(default=None, alias="class")
    autoflush: bool = (None,)
    expire_on_commit: bool = (None,)
    autobegin: bool = (None,)
    twophase: bool = (None,)
    enable_baked_queries: bool = (None,)
    info: dict[str, Any] = (None,)
    query_cls: DottedPath[Type[Query[Any]]] = (None,)
    join_transaction_mode: JoinTransactionMode = (None,)
    close_resets_only: bool = (None,)


class SqlAlchemySessionSettings(BaseModel):
    """Settings for the SQLAlchemy session defined in a settings file."""

    model_config = ConfigDict(extra="forbid")

    options: SqlAlchemySessionOptions = None
    binds: dict[DottedPath, str] = None


class SqlAlchemySettings(BaseModel):
    """Settings for the SQLAlchemy session defined in a settings file."""

    model_config = ConfigDict(extra="forbid")

    connections: dict[str, SqlAlchemyEngineSettings]
    session: SqlAlchemySessionSettings = Field(
        default_factory=SqlAlchemySessionSettings
    )
