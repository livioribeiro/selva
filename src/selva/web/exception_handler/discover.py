import inspect

from selva._util.package_scan import scan_packages
from selva.web.exception_handler.decorator import (
    ATTRIBUTE_EXCEPTION_HANDLER,
    ExceptionHandlerType,
)


def _is_exception_handler(arg) -> bool:
    return inspect.iscoroutinefunction(arg) and hasattr(
        arg, ATTRIBUTE_EXCEPTION_HANDLER
    )


def find_exception_handlers(*args) -> dict[type[Exception], ExceptionHandlerType]:
    result = {}

    for item in scan_packages(*args, predicate=_is_exception_handler):
        exc_handler_info = getattr(item, ATTRIBUTE_EXCEPTION_HANDLER)
        exc_type = exc_handler_info.exception_class
        if exc_type in result:
            raise ValueError("Exception handler already registered")
        result[exc_type] = item

    return result
