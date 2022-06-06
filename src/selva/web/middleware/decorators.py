import inspect
from collections.abc import Callable

from selva.di.decorators import service

MIDDLEWARE_ATTRIBUTE = "__selva_web_middleware__"


def middleware(target: type | Callable = None):
    def inner(arg):
        setattr(arg, MIDDLEWARE_ATTRIBUTE, True)
        if inspect.isclass(arg):
            service(arg)
        return arg

    return inner(target) if target else inner
