from importlib import import_module

__all__ = ("import_item",)


def import_item(name: str):
    """Import an item from a module"""

    match name.rsplit(".", 1):
        case [module_name, item_name]:
            module = import_module(module_name)
            if item := getattr(module, item_name, None):
                return item
            raise ImportError(
                f"module '{module.__name__}' does not have item '{item_name}'"
            )
        case _:
            raise ImportError("name must be in 'module.item' format")
