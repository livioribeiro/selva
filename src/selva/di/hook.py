import inspect
from collections.abc import Callable

from selva._util.package_scan import scan_packages
from selva.configuration.settings import Settings
from selva.di.container import Container

__all__ = ("hook", "run_hooks")

DI_ATTRIBUTE_HOOK = "__selva_di_hook__"


def hook(callback: Callable[[Container, Settings], None] | None) -> Callable:
    """Marks a function as a hook to the dependency injection container.

    Hook functions are called when the applications start, passing the dependency
    injection container and the application settings as parameters.
    """

    def inner(inner_callback):
        assert inspect.isfunction(inner_callback), "callback must be a function"

        sig = inspect.signature(inner_callback)
        assert len(sig.parameters) == 2, "callback must have 2 arguments"

        setattr(inner_callback, DI_ATTRIBUTE_HOOK, True)
        return inner_callback

    return inner(callback) if callback else inner


async def run_hooks(packages, container: Container, settings: Settings):
    hooks = scan_packages(packages, lambda x: getattr(x, DI_ATTRIBUTE_HOOK, False))
    for hook_func in hooks:
        maybe_awaitable = hook_func(container, settings)
        if inspect.isawaitable(maybe_awaitable):
            await maybe_awaitable
