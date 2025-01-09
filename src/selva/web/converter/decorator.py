from selva.di.decorator import service
from selva.web.converter.converter import Converter
from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_extractor import ParamExtractor


def register_from_request(target: type):
    def inner(cls):
        assert issubclass(cls, FromRequest)
        return service(cls, provides=FromRequest[target])

    return inner


def register_converter(source: type, target: type):
    def inner(cls):
        assert issubclass(cls, Converter)
        return service(cls, provides=Converter[source, target])

    return inner


def register_param_extractor(target: type):
    def inner(cls):
        assert issubclass(cls, ParamExtractor)
        return service(cls, provides=ParamExtractor[target])

    return inner
