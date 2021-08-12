import pytest

from dependency_injector import Container


@pytest.fixture
def ioc():
    return Container()
