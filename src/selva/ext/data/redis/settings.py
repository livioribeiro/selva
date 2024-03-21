from types import NoneType
from typing import Literal, Self, Type

from pydantic import BaseModel, ConfigDict, model_serializer, model_validator
from redis import RedisError

from selva._util.pydantic import DottedPath


class ConstantBackoffSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backoff: int


class ExponentialBackoffSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cap: int = None
    base: int = None


class BackoffSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    no_backoff: NoneType = None
    constant: ConstantBackoffSchema = None
    exponential: ExponentialBackoffSchema = None
    full_jitter: ExponentialBackoffSchema = None
    equal_jitter: ExponentialBackoffSchema = None
    decorrelated_jitter: ExponentialBackoffSchema = None

    @model_validator(mode="before")
    def validator(cls, data):
        if len(data) != 1:
            raise ValueError("Only one backoff value can be set")

        return data


class RetrySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backoff: BackoffSchema
    retries: int
    supported_errors: tuple[DottedPath[Type[RedisError]], ...] = None


class RedisOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    socket_timeout: float = None
    socket_connect_timeout: float = None
    socket_keepalive: bool = None
    socket_keepalive_options: dict[int, int | bytes] = None
    unix_socket_path: str = None
    encoding: str = None
    encoding_errors: Literal["strict", "ignore", "replace"] = None
    decode_responses: bool = None
    retry_on_timeout: bool = None
    retry_on_error: list = None
    ssl: bool = None
    ssl_keyfile: str = None
    ssl_certfile: str = None
    ssl_cert_reqs: str = None
    ssl_ca_certs: str = None
    ssl_ca_data: str = None
    ssl_check_hostname: bool = None
    max_connections: int = None
    single_connection_client: bool = None
    health_check_interval: int = None
    client_name: str = None
    lib_name: str = None
    lib_version: str = None
    retry: RetrySchema = None
    auto_close_connection_pool: bool = None
    protocol: int = None


class RedisSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = None
    host: str = None
    port: int = None
    db: int = None
    username: str = None
    password: str = None
    options: RedisOptions = None

    @model_validator(mode="after")
    def validator(self) -> Self:
        if self.url and (self.host or self.port or (self.db is not None)):
            raise ValueError(
                "Either 'url' should be provided, or 'host', 'port' and 'db'"
            )

        return self

    @model_serializer(when_used="unless-none")
    def serializer(self):
        data = {
            field: getattr(self, field)
            for field in set(self.model_fields_set)
            if field != "options"
        }

        if self.options:
            data |= self.options.model_dump(exclude_unset=True)

        return data
