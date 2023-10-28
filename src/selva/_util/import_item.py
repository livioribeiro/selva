from importlib import import_module

__all__ = ("import_item",)


def import_item(name: str):
    """Import an item from a module"""

    match name.rsplit(".", 1):
        case [module_name, item_name]:
            module = import_module(module_name)
            return getattr(module, item_name)
        case _:
            raise ValueError("name must be in 'module.item' format")
