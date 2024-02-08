from importlib import import_module

__all__ = ("import_item",)


def import_item(name: str):
    """Import a module or an item within a module using its name

    :param name: The name of the item to import, in the format 'package.module.item'.

    :return: The imported module or item within the module
    """

    try:
        return import_module(name)
    except ImportError as err:
        match name.rsplit(".", 1):
            case [module_name, item_name]:
                module = import_module(module_name)
                if item := getattr(module, item_name, None):
                    return item

                raise ImportError(
                    f"module '{module.__name__}' does not have item '{item_name}'"
                )

            case _:
                raise err
