from importlib import import_module
from pkgutil import resolve_name

__all__ = ("import_item",)


def import_item(name: str):
    """Import a module or an item within a module using its name

    :param name: The name of the item to import, in the format 'package.module[:item]'.

    :return: The imported module or item within the module
    """

    if ":" in name:
        return resolve_name(name)

    return import_module(name)
