from http import HTTPStatus

import pytest

from selva.web.error import (
    HTTPBadRequestException,
    HTTPForbiddenException,
    HTTPInternalServerException,
    HTTPNotFoundException,
    HTTPUnauthorizedException,
)


@pytest.mark.parametrize(
    "error_cls, status",
    [
        (HTTPBadRequestException, HTTPStatus.BAD_REQUEST),
        (HTTPNotFoundException, HTTPStatus.NOT_FOUND),
        (HTTPUnauthorizedException, HTTPStatus.UNAUTHORIZED),
        (HTTPForbiddenException, HTTPStatus.FORBIDDEN),
        (HTTPInternalServerException, HTTPStatus.INTERNAL_SERVER_ERROR),
    ],
    ids=[
        HTTPStatus.BAD_REQUEST.name,
        HTTPStatus.NOT_FOUND.name,
        HTTPStatus.UNAUTHORIZED.name,
        HTTPStatus.FORBIDDEN.name,
        HTTPStatus.INTERNAL_SERVER_ERROR.name,
    ],
)
def test_correct_status(error_cls, status: HTTPStatus):
    error = error_cls()
    assert error.status == status
