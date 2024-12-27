_empty = ()


class Lazy[T]:
    def __init__(
        self,
        di: "selva.di.container.Container",
        service: T,
        name: str | None = None,
        optional: bool = False
    ):
        self.__instance = _empty
        self.di = di
        self.service = service
        self.name = name
        self.optional = optional

    async def __call__(self) -> T:
        if self.__instance == _empty:
            self.__instance = await self.di.get(self.service, name=self.name, optional=self.optional)
        return self.__instance