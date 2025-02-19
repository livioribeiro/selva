from http import HTTPStatus

import pydantic
from pydantic import BaseModel as PydanticModel

from selva.web.http import Request
from selva.web.converter.decorator import register_converter
from selva.web.exception import HTTPBadRequestException, HTTPException


@register_converter(Request, PydanticModel)
class RequestPydanticConverter:
    async def convert(
        self,
        request: Request,
        original_type: type[PydanticModel],
    ) -> PydanticModel:
        # TODO: make request body decoding extensible
        content_type = request.headers.get("content-type")
        if content_type and "application/json" in content_type:
            data = await request.json()
        elif content_type and "application/x-www-form-urlencoded" in content_type:
            data = await request.form()
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
        original_type: type[list[PydanticModel]],
    ) -> list[PydanticModel]:
        content_type = request.headers.get("content-type")
        if content_type and "application/json" in content_type:
            data = await request.json()
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        adapter = pydantic.TypeAdapter(original_type)

        try:
            return adapter.validate_python(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err
