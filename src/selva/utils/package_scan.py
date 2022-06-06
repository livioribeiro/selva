import importlib
import inspect
import pkgutil
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any


def _is_class_or_function(arg) -> bool:
    return inspect.isclass(arg) or inspect.isfunction(arg)


def _scan_members(module, predicate):
    for _name, member in inspect.getmembers(module, predicate):
        if member.__module__ == module.__name__:
            yield member


def scan_packages(
    modules_to_scan: Iterable[str | ModuleType],
    predicate: Callable[[Any], bool] = None,
) -> Iterable[type]:
    for module in modules_to_scan:
        if isinstance(module, str):
            module = importlib.import_module(module)

        if predicate:

            def scan_predicate(arg):
                return _is_class_or_function(arg) and predicate(arg)

        else:
            scan_predicate = _is_class_or_function

        yield from _scan_members(module, scan_predicate)

        spec = getattr(module, "__spec__", None)
        if not spec or not spec.submodule_search_locations:
            # module is not a package
            continue

        search_paths = spec.submodule_search_locations

        prefix = spec.name
        if prefix:
            prefix += "."

        for _module_finder, name, _ispkg in pkgutil.walk_packages(search_paths, prefix):
            submodule = importlib.import_module(name)
            yield from _scan_members(submodule, scan_predicate)
