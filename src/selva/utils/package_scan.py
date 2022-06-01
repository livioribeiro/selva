import importlib
import inspect
import pkgutil
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any


def scan_packages(
    modules_to_scan: Iterable[str | ModuleType],
    predicate: Callable[[Any], bool] = None,
) -> Iterable[type]:
    for module_to_scan in modules_to_scan:
        if isinstance(module_to_scan, str):
            module_to_scan = importlib.import_module(module_to_scan)

        for _name, member in inspect.getmembers(module_to_scan, predicate):
            yield member

        spec = getattr(module_to_scan, "__spec__", None)
        if not spec or not spec.submodule_search_locations:
            # module is not a package
            continue

        search_paths = spec.submodule_search_locations

        prefix = spec.name
        if prefix:
            prefix += "."

        for _module_finder, name, _ispkg in pkgutil.walk_packages(search_paths, prefix):
            module = importlib.import_module(name)
            for _name, member in inspect.getmembers(module, predicate):
                yield member
