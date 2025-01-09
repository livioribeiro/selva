from collections.abc import Awaitable
from typing import Any, Protocol, TypeVar, runtime_checkable

from asgikit.requests import Request

__all__ = ("FromRequest",)

T = TypeVar("T")


@runtime_checkable
class FromRequest(Protocol[T]):
    """Base class for services that extract values from the request"""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def from_request(
        self,
        request: Request,
        original_type: type[T],
        parameter_name: str,
        metadata: Any,
        optional: bool,
    ) -> T | Awaitable[T]:
        """Extract values from the request based on the type hint

        The `FromRequest` implementation may be for a superclass of the declared
        type, therefore the original type is passed as a parameter

        :param request: The request to extract values from
        :param original_type: Declared type on handler method signature
        :param parameter_name: Name of the parameter on the handler method
        :param metadata: Any metadata associated with the type
        :param optional: Whether the parameter is optional
        """
