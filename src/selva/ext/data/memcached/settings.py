from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from selva._util.pydantic import DottedPath


class MemcachedOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pool_size: int = None
    pool_minsize: int = None
    get_flat_handler: DottedPath[Callable] = None
    set_flat_handler: DottedPath[Callable] = None
    conn_args: DottedPath[dict] = None


class MemcachedSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str
    options: MemcachedOptions = None
