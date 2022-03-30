from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Lazy(Generic[T]):
    def __init__(self, container, service: type, context: Any = None):
        self.__container = container
        self.__service = service
        self.__context = context
        self.__instance: T = None

    async def get(self) -> T:
        if self.__instance is None:
            self.__instance = await self.__container.get(
                self.__service, context=self.__context
            )

        return self.__instance
