import pytest
from asgikit.requests import Request
from asgikit.responses import Response

from selva.web.middleware import Middleware


class Mid(Middleware):
    async def __call__(self, chain, request: Request, response: Response):
        await chain(request, response)


async def test_non_async_chain_should_fail():
    mid = Mid()

    def chain_call(request, response):
        pass

    with pytest.raises(TypeError):
        await mid(chain_call, None, None)
