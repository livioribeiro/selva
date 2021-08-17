import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Generator, Iterable, Union


def find_injectables(
    module: ModuleType,
) -> Generator[type, None, None]:
    for _, i in inspect.getmembers(module):
        if hasattr(i, "__dependency_injector__"):
            yield i


def scan_packages(
    *modules_to_scan: Union[str, ModuleType],
) -> Iterable[type]:
    for module_to_scan in modules_to_scan:
        if isinstance(module_to_scan, str):
            module_to_scan = importlib.import_module(module_to_scan)

        yield from find_injectables(module_to_scan)

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
            yield from find_injectables(module)
