import pytest

from selva.web.middleware import Middleware


class Mid(Middleware):
    async def __call__(self, context):
        return await self.app(context)


async def test_set_app():
    async def app(ctx):
        return ctx

    mid = Mid()
    mid.set_app(app)

    result = await mid(1)
    assert result == 1


async def test_non_async_app_should_raise_error():
    def app(ctx):
        return ctx

    mid = Mid()
    mid.set_app(app)

    with pytest.raises(TypeError):
        await mid(None)


async def test_set_app_not_called_should_raise_error():
    mid = Mid()
    with pytest.raises(RuntimeError):
        await mid(None)