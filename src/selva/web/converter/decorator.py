from typing import Type

from selva.di.decorator import service
from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_converter import ParamConverter
from selva.web.converter.param_extractor import ParamExtractor


def register_from_request(target: Type):
    def inner(cls):
        assert issubclass(cls, FromRequest)
        return service(cls, provides=FromRequest[target])

    return inner


def register_param_converter(target: Type):
    def inner(cls):
        if not hasattr(cls, ParamConverter.into_str.__name__):
            setattr(cls, ParamConverter.into_str.__name__, ParamConverter.into_str)

        assert issubclass(cls, ParamConverter)
        return service(cls, provides=ParamConverter[target])

    return inner


def register_param_extractor(target: Type):
    def inner(cls):
        assert issubclass(cls, ParamExtractor)
        return service(cls, provides=ParamExtractor[target])

    return inner
