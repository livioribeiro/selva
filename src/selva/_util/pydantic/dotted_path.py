import typing
from typing import Any, Generic, TypeVar

from pydantic import GetCoreSchemaHandler, ValidatorFunctionWrapHandler
from pydantic_core import PydanticCustomError, core_schema

from selva._util.import_item import import_item

T = TypeVar("T")


class DottedPath(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        origin = typing.get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            item_tp = Any
        else:
            item_tp = typing.get_args(source_type)[0]

        item_schema = handler.generate_schema(Any)

        def validate_from_str(
            value: str, function_handler: ValidatorFunctionWrapHandler
        ) -> item_tp:
            try:
                item = import_item(value)
            except ImportError as e:
                raise PydanticCustomError(
                    "invalid_dotted_path",
                    "unable to import '{path}': {error}",
                    {"path": value, "error": e.msg},
                ) from e

            return function_handler(item)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_wrap_validator_function(
                    validate_from_str, item_schema
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_subclass_schema(str),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: f"{instance.__module__}.{instance.__qualname__}",
                when_used="json-unless-none",
            ),
        )
