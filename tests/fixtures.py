import ward

from dependency_injector import Container


@ward.fixture
def ioc():
    return Container()
