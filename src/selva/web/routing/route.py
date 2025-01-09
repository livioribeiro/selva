import re
import typing
from collections import Counter
from http import HTTPMethod
from re import Pattern
from typing import Callable, NamedTuple

__all__ = ("Route", "RouteMatch")

RE_PATH_PARAM_SPEC = re.compile(r"([:*])([a-zA-Z\w]+)")
RE_MULTI_SLASH = re.compile(r"/{2,}")

PATH_PARAM_PATTERN = {
    ":": r"[^/]+?",
    "*": r".*",
}


def build_path_regex_and_params(
    handler: Callable, path: str
) -> tuple[Pattern, dict[str, type]]:
    """parse path and build regex for route matching

    :returns: compiled regex and tuple of mapping param name to type
    """

    type_hints = typing.get_type_hints(handler)
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


class Route:
    def __init__(
        self,
        method: HTTPMethod | None,
        path: str,
        action: Callable,
        name: str,
    ):
        self.method = method
        self.path = path
        self.action = action
        self.name = name
        self.regex, self.path_params = build_path_regex_and_params(action, path)

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
