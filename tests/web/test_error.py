from http import HTTPStatus

import pytest

from selva.web.error import (
    HTTPBadRequestError,
    HTTPForbiddenError,
    HTTPInternalServerError,
    HTTPNotFoundError,
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
