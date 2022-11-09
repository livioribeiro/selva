import json
import os
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Optional, TypeVar

T = TypeVar("T")

_UNSET = ()


def get_str(key: str, default: Optional[str] = _UNSET) -> str:
    if value := os.getenv(key):
        return value

    if default is not _UNSET:
        return default

    raise KeyError(f"Environment variable '{key}' is not defined")


def _get_env_and_convert(
    key: str, default: Optional[T], converter: Callable[[str], T], type_name: str
) -> T:
    value = get_str(key, default)

    try:
        return converter(value)
    except ValueError as err:
        message = (
            f"Environment variable '{key}'"
            f" is not compatible with type '{type_name}': '{value}'"
        )
        raise ValueError(message) from err


def get_int(key: str, default: Optional[int] = _UNSET) -> int:
    return _get_env_and_convert(key, default, int, "int")


def get_float(key: str, default: Optional[float] = _UNSET) -> float:
    return _get_env_and_convert(key, default, float, "float")


def _bool_converter(value: str) -> bool:
    if value in ("1", "true", "True"):
        return True

    if value in ("0", "false", "False"):
        return False

    raise ValueError(
        "bool value must be one of ['1', 'true', 'True', '0', 'false', 'False']"
    )


def get_bool(key: str, default: Optional[bool] = _UNSET) -> bool:
    return _get_env_and_convert(key, default, _bool_converter, "bool")


def _list_converter(value: str) -> list[str]:
    return [v.strip().strip("'\"") for v in value.split(",")]


def get_list(key: str, default: Optional[Sequence[str]] = _UNSET) -> Sequence[str]:
    return _get_env_and_convert(key, default, _list_converter, "list")


def _dict_converter(value: str) -> dict[str, str]:
    result: dict[str, str] = {}

    for item in value.split(","):
        match item.split("=", maxsplit=1):
            case [key, val]:
                key = key.strip().strip("'\"")
                val = val.strip().strip("'\"")
                result[key] = val
            case _:
                message = f"{item} is not a valid dict item"
                raise ValueError(message)

    return result


def get_dict(key, default: Optional[Mapping[str, str]] = _UNSET) -> Mapping[str, str]:
    return _get_env_and_convert(key, default, _dict_converter, "dict")


def _json_converter(value: str) -> dict[str, Any]:
    return json.loads(value)


def get_json(key, default: Optional[Mapping[str, Any]] = _UNSET) -> Mapping[str, Any]:
    return _get_env_and_convert(key, default, _json_converter, "json")
