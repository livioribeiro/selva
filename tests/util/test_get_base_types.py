from typing import Generic, Protocol, TypeVar

import pytest

from selva._util.base_types import get_base_types

T1 = TypeVar("T1")
T2 = TypeVar("T2")


class Interface1(Generic[T1]):
    pass


class Interface2(Interface1[int], Generic[T2]):
    pass


class Impl1(Interface1[int]):
    pass


class Impl12(Impl1):
    pass


class Impl2(Interface2[str]):
    pass


class Impl22(Impl2):
    pass


class Proto1(Protocol[T1]):
    pass


class ProtoImpl1(Proto1[str]):
    pass


@pytest.mark.parametrize(
    "base_type,expected",
    [
        (Impl12, [Impl12, Impl1, Interface1[int], Interface1]),
        (
            Impl22,
            [Impl22, Impl2, Interface2[str], Interface2, Interface1[int], Interface1],
        ),
        (Interface1[str], [Interface1[str], Interface1]),
        (Interface2[str], [Interface2[str], Interface2, Interface1[int], Interface1]),
        (ProtoImpl1, [ProtoImpl1, Proto1[str], Proto1]),
    ],
    ids=[
        "1 level generic",
        "2 levels generic",
        "1 level interface input",
        "2 levels interface input",
        "Using 'Protocol'",
    ],
)
def test_get_base_types(base_type, expected):
    base_types = get_base_types(base_type)
    assert base_types == expected
