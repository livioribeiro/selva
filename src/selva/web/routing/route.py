import re
import typing
from collections import Counter
from re import Pattern
from typing import Callable, NamedTuple

from selva.web.requests import HTTPMethod

__all__ = ("Route", "RouteMatch")

RE_PATH_PARAM_SPEC = re.compile(r"([:*])([a-zA-Z\w]+)")
RE_MULTI_SLASH = re.compile(r"/{2,}")

PATH_PARAM_PATTERN = {
    ":": r".+?",
    "*": r".*",
}


def build_path_regex(
    path: str, type_hints: dict[str, type]
) -> tuple[dict[str, type], Pattern]:
    """parse path and build regex for route matching

    :returns: tuple of mapping param name to type and compiled regex
    """
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
    return param_types, re.compile(regex)


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

        type_hints = typing.get_type_hints(action)
        type_hints.pop("return", None)

        self.path_params, self.regex = build_path_regex(self.path, type_hints)
        self.request_params = {
            name: param_type
            for name, param_type in type_hints.items()
            if name not in self.path_params
        }

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
