from typing import NamedTuple


class Inject(NamedTuple):
    """Defines a service dependency"""

    name: str = None
