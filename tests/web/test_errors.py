from http import HTTPStatus

import pytest

from selva.web.errors import (
    HTTPBadRequestError,
    HTTPClientError,
    HTTPForbiddenError,
    HTTPInternalServerError,
    HTTPNotFoundError,
    HTTPServerError,
    HTTPUnauthorizedError,
)


@pytest.mark.parametrize(
    "error_cls, status",
    [
        (HTTPBadRequestError, HTTPStatus.BAD_REQUEST),
        (HTTPNotFoundError, HTTPStatus.NOT_FOUND),
        (HTTPUnauthorizedError, HTTPStatus.UNAUTHORIZED),
        (HTTPForbiddenError, HTTPStatus.FORBIDDEN),
        (HTTPInternalServerError, HTTPStatus.INTERNAL_SERVER_ERROR),
    ],
    ids=[
        HTTPStatus.BAD_REQUEST.name,
        HTTPStatus.NOT_FOUND.name,
        HTTPStatus.UNAUTHORIZED.name,
        HTTPStatus.FORBIDDEN.name,
        HTTPStatus.INTERNAL_SERVER_ERROR.name,
    ],
)
def test_correct_status_code(error_cls, status: HTTPStatus):
    error = error_cls()
    assert error.status_code == status


@pytest.mark.parametrize(
    "error_cls, status_code",
    [
        (HTTPClientError, 300),
        (HTTPClientError, 500),
        (HTTPServerError, 400),
        (HTTPServerError, 600),
    ],
)
def test_base_error_with_wrong_status_code_should_raise_error(error_cls, status_code):
    with pytest.raises(ValueError):
        error_cls(status_code)
