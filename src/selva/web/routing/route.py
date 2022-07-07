import re
import typing
from collections import Counter
from re import Pattern
from typing import Callable, NamedTuple

from asgikit.requests import HttpMethod

PATH_PARAM_SPEC_RE = re.compile(r"\{([a-zA-Z\w]+)\}")
PATH_PARAM_PATTERN = r".+?"


def build_path_regex(
    path: str, type_hints: dict[str, type]
) -> tuple[dict[str, type], Pattern]:
    """parse path and build regex for route matching

    :returns: tuple of mapping param name to type and compiled regex
    """
    regex = path

    path_params = PATH_PARAM_SPEC_RE.findall(path)

    # verify that path does not have duplicate parameters
    counter = Counter(path_params)
    for name, occurencies in counter.items():
        if occurencies > 1:
            raise ValueError(
                f"path parameter '{name}' occurred more than once ({occurencies} times)"
            )

    param_types = {}
    for param in path_params:
        type_hint = type_hints.get(param, str)
        param_types[param] = type_hint

        param_regex = f"(?P<{param}>{PATH_PARAM_PATTERN})"
        regex = regex.replace(f"{{{param}}}", param_regex)

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
        method: HttpMethod | None,
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

    def match(self, method: HttpMethod | None, path: str) -> dict[str, str] | None:
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
    method: HttpMethod | None
    path: str
    params: dict[str, str]
