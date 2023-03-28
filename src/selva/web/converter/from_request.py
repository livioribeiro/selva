from collections.abc import Awaitable
from typing import Protocol, Type, TypeVar, runtime_checkable

from selva.web.context import RequestContext

__all__ = ("FromRequest",)

T = TypeVar("T")


@runtime_checkable
class FromRequest(Protocol[T]):
    """Base class for services that extract values from the request"""

    def from_request(
        self, context: RequestContext, original_type: Type[T], parameter_name: str
    ) -> T | Awaitable[T]:
        """Extract values from the request based on the type hint

        The `FromRequest` implementation may be for a superclass of the declared
        type, therefore the original type is passed as a parameter

        :param context: The request context to extract values from
        :param original_type: Declared type on handler method signature
        :param parameter_name: Name of the parameter on the handler method
        """

        raise NotImplementedError()
