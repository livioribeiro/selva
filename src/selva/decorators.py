from collections.abc import Callable

BLOCKING_ATTRIBUTE = "_blocking_"


def blocking(target: Callable) -> Callable:
    setattr(target, BLOCKING_ATTRIBUTE, True)
    return target
