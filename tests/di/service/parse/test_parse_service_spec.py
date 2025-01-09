import pytest

from selva.di.error import InvalidServiceTypeError
from selva.di.service.parse import _get_service_signature, parse_service_spec


def test_parse_invalid_service_should_fail():
    with pytest.raises(InvalidServiceTypeError):
        parse_service_spec(object())


def test_get_dependencies_invalid_service_should_fail():
    with pytest.raises(InvalidServiceTypeError):
        list(_get_service_signature(object()))
