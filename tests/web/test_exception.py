from http import HTTPStatus

import pytest

from selva.web.exception import (
    HTTPBadRequestException,
    HTTPException,
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
    assert error.status_code == status


def test_custom_http_exception():
    error = HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)
    assert error.status_code == HTTPStatus.IM_A_TEAPOT
