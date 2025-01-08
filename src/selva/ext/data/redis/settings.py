import socket
from types import NoneType
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from redis.backoff import (
    AbstractBackoff,
    ConstantBackoff,
    DecorrelatedJitterBackoff,
    EqualJitterBackoff,
    ExponentialBackoff,
    FullJitterBackoff,
    NoBackoff,
)
from redis.retry import Retry

from selva._util.pydantic import DottedPath


class NoBackoffSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


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
    @classmethod
    def verify_backoff(cls, data):
        if len(data) != 1:
            raise ValueError("Only one backoff value can be set")

        return data


class RetrySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backoff: BackoffSchema
    retries: int
    supported_errors: tuple[DottedPath[type[Exception]], ...] = None

    @staticmethod
    def build_backoff(backoff: BackoffSchema) -> AbstractBackoff:
        if "no_backoff" in backoff.model_fields_set:
            return NoBackoff()

        if value := backoff.constant:
            return ConstantBackoff(**value.model_dump(exclude_unset=True))

        if value := backoff.exponential:
            return ExponentialBackoff(**value.model_dump(exclude_unset=True))

        if value := backoff.full_jitter:
            return FullJitterBackoff(**value.model_dump(exclude_unset=True))

        if value := backoff.equal_jitter:
            return EqualJitterBackoff(**value.model_dump(exclude_unset=True))

        if value := backoff.decorrelated_jitter:
            return DecorrelatedJitterBackoff(**value.model_dump(exclude_unset=True))

        raise ValueError("No value defined for 'backoff'")

    @model_serializer(when_used="unless-none")
    def serialize_model(self) -> dict[str, Any]:
        result = {
            "backoff": self.build_backoff(self.backoff),
            "retries": self.retries,
        }

        if supported_errors := self.supported_errors:
            result["supported_errors"] = supported_errors

        return result


class SocketKeepaliveOptions(BaseModel):
    tcp_keepidle: Annotated[int, Field(alias="TCP_KEEPIDLE")] = None
    tcp_keepcnt: Annotated[int, Field(alias="TCP_KEEPCNT")] = None
    tcp_keepintvl: Annotated[int, Field(alias="TCP_KEEPINTVL")] = None

    @model_serializer(when_used="unless-none")
    def serialize_model(self) -> dict[int, int]:
        result = {}
        if self.tcp_keepidle:
            result[socket.TCP_KEEPIDLE] = self.tcp_keepidle
        if self.tcp_keepcnt:
            result[socket.TCP_KEEPCNT] = self.tcp_keepcnt
        if self.tcp_keepintvl:
            result[socket.TCP_KEEPINTVL] = self.tcp_keepintvl
        return result


class RedisOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    socket_timeout: float = None
    socket_connect_timeout: float = None
    socket_keepalive: bool = None
    socket_keepalive_options: dict[
        Literal["TCP_KEEPIDLE", "TCP_KEEPCNT", "TCP_KEEPINTVL"], int
    ] = None
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

    @model_serializer(when_used="unless-none", mode="wrap")
    def serialize_model(self, nxt):
        result = nxt(self)
        if retry := result.get("retry"):
            result["retry"] = Retry(**retry)
        return result


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
    def verify_either_url_or_components(self) -> Self:
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
