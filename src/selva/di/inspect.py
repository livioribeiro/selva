from selva.di.decorator import DI_ATTRIBUTE_SERVICE, DI_ATTRIBUTE_RESOURCE


def is_service(arg) -> bool:
    return hasattr(arg, DI_ATTRIBUTE_SERVICE)


def is_resource(arg) -> bool:
    return hasattr(arg, DI_ATTRIBUTE_RESOURCE)
