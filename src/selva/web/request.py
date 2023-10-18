import typing
from http import HTTPMethod, HTTPStatus

from asgikit.requests import Request as BaseRequest, read_form, read_json

import pydantic
from pydantic import BaseModel as PydanticModel

from selva.di.container import Container
from selva.web.converter import Converter
from selva.web.exception import HTTPException, HTTPBadRequestException


__all__ = ("Request",)


class Request(BaseRequest):
    def __init__(self, scope, receive, send, di: Container):
        super().__init__(scope, receive, send)
        self.di = di

    async def get_query_param[T](self, name: str) -> T:
        data = self.query.get(name)
        converter = await self.di.get(Converter[T])
        return await converter.from_str(data)

    async def get_header[T](self, name: str) -> T:
        data = self.headers.get(name)
        converter = await self.di.get(Converter[T])
        return await converter.from_str(data)


async def read_model[T: PydanticModel | list[PydanticModel]](request: BaseRequest) -> T:
    if request.method not in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
        # TODO: improve error
        raise Exception(
            "Pydantic model parameter on method that does not accept body"
        )

    # TODO: make request body decoding extensible
    try:
        if typing.get_origin(T) is list:
            if "application/json" in request.content_type:
                adapter = pydantic.TypeAdapter(T)
                data = await read_json(request)
                return adapter.validate_python(data)
            else:
                raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        else:
            if "application/json" in request.content_type:
                data = await read_json(request)
            elif "application/x-www-form-urlencoded" in request.content_type:
                data = await read_form(request)
            else:
                raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

            return T.model_validate(data)
    except pydantic.ValidationError as err:
        raise HTTPBadRequestException() from err
