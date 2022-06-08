import inspect

MIDDLEWARE_ATTRIBUTE = "__selva_web_middleware__"


def middleware(target: type = None):
    def inner(arg):
        if not inspect.isclass(arg):
            raise ValueError("Middleware must be a class")

        setattr(arg, MIDDLEWARE_ATTRIBUTE, True)
        return arg

    return inner(target) if target else inner
