import pytest

from selva.web.context import RequestContext
from selva.web.request import HTTPMethod


def test_wrong_context_should_fail():
    scope = {"type": "wrong"}

    with pytest.raises(AssertionError):
        RequestContext(scope, None, None)


def test_request_on_http_scope_is_not_none():
    scope = {"type": "http"}
    context = RequestContext(scope, None, None)
    assert context.request is not None
    assert context.websocket is None


def test_websocket_on_websocket_scope_is_not_none():
    scope = {"type": "websocket"}
    context = RequestContext(scope, None, None)
    assert context.websocket is not None
    assert context.request is None


@pytest.mark.parametrize("method", HTTPMethod)
def test_method_on_http_scope(method):
    scope = {
        "type": "http",
        "method": method.name,
    }

    context = RequestContext(scope, None, None)
    assert context.method == method


def test_method_on_websocket_scope():
    scope = {"type": "websocket"}
    context = RequestContext(scope, None, None)
    assert context.method is None