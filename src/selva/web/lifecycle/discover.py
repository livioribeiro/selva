from selva._util.package_scan import scan_packages
from selva.web.lifecycle.decorator import ATTRIBUTE_BACKGROUND, ATTRIBUTE_STARTUP


def _predicate_startup_hooks(item) -> bool:
    return getattr(item, ATTRIBUTE_STARTUP, False)


def _predicate_background_services(item) -> bool:
    return getattr(item, ATTRIBUTE_BACKGROUND, False)


def find_startup_hooks(*args):
    return list(scan_packages(*args, predicate=_predicate_startup_hooks))


def find_background_services(*args):
    return list(scan_packages(*args, predicate=_predicate_background_services))
