import pytest
from asgikit.requests import Request

from selva.web.middleware import Middleware


class Mid(Middleware):
    async def __call__(self, chain, request: Request):
        await chain(request)


async def test_non_async_chain_should_fail():
    mid = Mid()

    def chain_call(request, response):
        pass

    with pytest.raises(TypeError):
        await mid(chain_call, None, None)
