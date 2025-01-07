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

    try:
        return import_module(name)
    except ImportError as err:
        match name.rsplit(".", maxsplit=1):
            case [mod, item]:
                return resolve_name(f"{mod}:{item}")
            case _:
                raise err
