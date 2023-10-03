import pytest
from asgikit.requests import Request
from asgikit.responses import Response

from selva.web.middleware import Middleware


class Mid(Middleware):
    async def __call__(self, request: Request, response: Response):
        await self.app(request, response)


async def test_set_app():
    result = 0

    async def app(req, res):
        nonlocal result
        result = req + res

    mid = Mid()
    mid.set_app(app)

    await mid(1, 2)
    assert result == 3


async def test_non_async_app_should_fail():
    def app(ctx):
        return ctx

    mid = Mid()
    mid.set_app(app)

    with pytest.raises(TypeError):
        await mid(None, None)


async def test_set_app_not_called_should_fail():
    mid = Mid()
    with pytest.raises(RuntimeError):
        await mid(None, None)
