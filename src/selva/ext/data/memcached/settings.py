from typing import Type

from emcache import ClusterEvents
from pydantic import BaseModel, ConfigDict

from selva._util.pydantic import DottedPath


class MemcachedOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timeout: float = None
    max_connections: int = None
    min_connections: int = None
    purge_unused_connections_after: float = None
    connection_timeout: float = None
    cluster_events: DottedPath[Type[ClusterEvents]] = None
    purge_unhealthy_nodes: bool = None
    autobatching: bool = None
    autobatching_max_keys: bool = None
    ssl: bool = None
    ssl_verify: bool = None
    ssl_extra_ca: str = None
    autodiscovery: bool = None
    autodiscovery_poll_interval: float = None
    autodiscovery_timeout: float = None


class MemcachedSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str
    options: MemcachedOptions = None
