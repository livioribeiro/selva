import pytest

from selva.di.container import Container


@pytest.fixture
async def ioc() -> Container:
    return Container()
