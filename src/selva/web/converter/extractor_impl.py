from dataclasses import dataclass

from starlette.datastructures import FormData

from selva.web.converter.extractor import Extractor, ExtractorArgs
from selva.web.context import RequestContext


@dataclass(kw_only=True, eq=False, match_args=False)
class Header:
    name: str = None
    optional: bool = True


class HeaderExtractor(Extractor[Header]):
    def extract(self, context: RequestContext, args: ExtractorArgs[Header]) -> str:
        name = args.arg_value.name or args.arg_name
        value = context.headers.get(name)

        if not value and not args.arg_value.optional:
            raise KeyError(name)

        return value


@dataclass(kw_only=True, eq=False, match_args=False)
class HeaderList:
    name: str = None
    optional: bool = True


class HeaderListExtractor(Extractor[Header]):
    def extract(self, context: RequestContext, args: ExtractorArgs[Header]) -> list[str]:
        name = args.arg_value.name or args.arg_name
        value = context.headers.getlist(name)

        if not value and not args.arg_value.optional:
            raise KeyError(name)

        return value


class Form:
    pass


class FormExtractor(Extractor[Form, FormData]):
    async def extract(self, context: RequestContext, args: ExtractorArgs[Form]) -> FormData:
        if request := context.request:
            return await request.form()

        raise RuntimeError()


class Json:
    pass


class JsonExtractor(Extractor[Json, dict]):
    async def extract(self, context: RequestContext, args: ExtractorArgs[Json]) -> dict:
        if request := context.request:
            return await request.json()

        raise RuntimeError()
