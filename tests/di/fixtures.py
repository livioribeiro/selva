import pytest

from selva.di import Container


@pytest.fixture
async def ioc() -> Container:
    return Container()
