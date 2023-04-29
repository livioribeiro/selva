import inspect
import re
import typing
from collections import Counter
from collections.abc import Iterable
from re import Pattern
from typing import Annotated, Any, Callable, NamedTuple

from selva.web.request import HTTPMethod

__all__ = ("Route", "RouteMatch")

RE_PATH_PARAM_SPEC = re.compile(r"([:*])([a-zA-Z\w]+)")
RE_MULTI_SLASH = re.compile(r"/{2,}")

PATH_PARAM_PATTERN = {
    ":": r".+?",
    "*": r".*",
}


def build_path_regex_and_params(
    action: Callable, path: str
) -> tuple[Pattern, dict[str, type]]:
    """parse path and build regex for route matching

    :returns: compiled regex and tuple of mapping param name to type
    """

    type_hints = typing.get_type_hints(action)
    type_hints.pop("return", None)

    regex = RE_MULTI_SLASH.sub("/", path)
    path_params = RE_PATH_PARAM_SPEC.findall(path)

    # verify that path does not have duplicate parameters
    counter = Counter(path_params)
    repeated = [name for name, occurrencies in counter.items() if occurrencies > 1]
    if repeated:
        raise ValueError(
            f"path parameters defined more than once: {', '.join(repeated)}"
        )

    param_types = {}
    for kind, param in path_params:
        type_hint = type_hints.get(param, str)
        param_types[param] = type_hint

        param_regex = f"(?P<{param}>{PATH_PARAM_PATTERN[kind]})"
        regex = regex.replace(f"{kind}{param}", param_regex)

    if not regex.startswith("/"):
        regex = "/" + regex

    if regex.endswith("/"):
        regex += "?"
    else:
        regex += "/?"

    regex = f"^{regex}$"
    return re.compile(regex), param_types


def build_request_params(
    action: Callable, path_params: Iterable[str]
) -> dict[str, tuple[type, Any | None]]:
    type_hints = typing.get_type_hints(action, include_extras=True)
    type_hints.pop("return", None)

    for path_param in path_params:
        type_hints.pop(path_param, None)

    result = {}

    for name, type_hint in type_hints.items():
        if typing.get_origin(type_hint) is Annotated:
            # Annotated is garanteed to have at least 2 args
            param_type, param_meta, *_ = typing.get_args(type_hint)
            if inspect.isclass(param_meta):
                # TODO: improve error
                raise Exception(
                    f"Annotation on parameter '{name}' must be an instance of class '{param_meta}, "
                    "not the class itself'"
                )
            result[name] = (param_type, param_meta)
        else:
            result[name] = (type_hint, None)

    return result


class Route:
    def __init__(
        self,
        method: HTTPMethod | None,
        path: str,
        controller: type,
        action: Callable,
        name: str,
    ):
        self.method = method
        self.path = path
        self.controller = controller
        self.action = action
        self.name = name

        self.regex, self.path_params = build_path_regex_and_params(action, path)
        self.request_params = build_request_params(action, self.path_params.keys())

    def match(self, method: HTTPMethod | None, path: str) -> dict[str, str] | None:
        if method is self.method and (match := self.regex.match(path)):
            return match.groupdict()

        return None

    def reverse(self, **kwargs) -> str:
        path = self.path

        for param, value in kwargs.items():
            if param not in self.path_params:
                raise ValueError()
            path = path.replace(f"{{{param}}}", value)

        return path


class RouteMatch(NamedTuple):
    route: Route
    method: HTTPMethod | None
    path: str
    params: dict[str, str]
