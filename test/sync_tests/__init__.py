import asyncio

import pytest

from dependency_injector import SyncContainer


@pytest.fixture
def ioc():
    return SyncContainer(loop=asyncio.new_event_loop())
