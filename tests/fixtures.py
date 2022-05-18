import ward

from dependency_injector import Container


@ward.fixture
async def ioc():
    return Container()
