from http import HTTPMethod, HTTPStatus
from typing import Type

import pydantic
from asgikit.requests import Request, read_form, read_json
from pydantic import BaseModel as PydanticModel

from selva.di.decorator import service
from selva.web.converter.from_request import FromRequest
from selva.web.exception import HTTPBadRequestException, HTTPException


@service
async def pydantic_model_from_request(_) -> FromRequest[PydanticModel]:
    return PydanticModelFromRequest()


@service
async def pydanto_model_list_from_request(_) -> FromRequest[list[PydanticModel]]:
    return PydanticModelListFromRequest()


class PydanticModelFromRequest:
    async def from_request(
        self,
        request: Request,
        original_type: Type[PydanticModel],
        _parameter_name,
        _metadata=None,
    ) -> PydanticModel:
        if request.method not in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
            raise TypeError(
                "Pydantic model parameter on method that does not accept body"
            )

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


class PydanticModelListFromRequest:
    async def from_request(
        self,
        request: Request,
        original_type: Type[list[PydanticModel]],
        _parameter_name,
        _metadata=None,
    ) -> list[PydanticModel]:
        if request.method not in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
            raise TypeError("Pydantic parameter on method that does not accept body")

        if "application/json" in request.content_type:
            data = await read_json(request)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        adapter = pydantic.TypeAdapter(original_type)

        try:
            return adapter.validate_python(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err
