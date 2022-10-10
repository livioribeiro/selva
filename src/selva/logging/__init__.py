import inspect

from .logger import Logger


def get_logger() -> Logger:
    logger_name = None

    stack = iter(inspect.stack())
    while frame_info := next(stack):
        if frame_info.filename == __file__:
            frame_info = next(stack)

            f_locals = frame_info.frame.f_locals
            f_globals = frame_info.frame.f_globals
            logger_name = (
                f_locals.get("__module__")
                or f_locals.get("__name__")
                or f_globals.get("__name__")
            )

            break

    return Logger(logger_name)
