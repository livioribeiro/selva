from abc import ABC
from collections.abc import Mapping


class Json(Mapping, ABC):
    pass


class Form(Mapping, ABC):
    pass
