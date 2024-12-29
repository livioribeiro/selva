from http import HTTPStatus

import pydantic
from asgikit.requests import Request, read_form, read_json
from pydantic import BaseModel as PydanticModel

from selva.web.converter.decorator import register_converter
from selva.web.exception import HTTPBadRequestException, HTTPException


@register_converter(Request, dict)
class RequestDictConverter:
    async def convert(self, request: Request, original_type: type) -> dict:
        if "application/json" in request.content_type:
            return await read_json(request)
        elif "application/x-www-form-urlencoded" in request.content_type:
            return await read_form(request)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


@register_converter(Request, PydanticModel)
class RequestPydanticConverter:
    async def convert(
        self,
        request: Request,
        original_type: type,
    ) -> PydanticModel:
        # TODO: make request body decoding extensible
        if "application/json" in request.content_type:
            data = await read_json(request)
        elif "application/x-www-form-urlencoded" in request.content_type:
            data = await read_form(request)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            return original_type.model_validate(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err


@register_converter(Request, list[PydanticModel])
class RequestPydanticListConverter:
    async def convert(
        self,
        request: Request,
        original_type: list[type[PydanticModel]],
    ) -> list[PydanticModel]:
        if "application/json" in request.content_type:
            data = await read_json(request)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        adapter = pydantic.TypeAdapter(original_type)

        try:
            return adapter.validate_python(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err