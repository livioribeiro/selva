import inspect

import pytest

from selva._util.package_scan import scan_packages


def test_scan_package():
    from . import package_to_scan

    result = list(scan_packages(package_to_scan))

    from .package_to_scan.module_to_scan import ClassItem, function_item

    assert result == [ClassItem, function_item]


def test_scan_package_str():
    result = list(scan_packages("tests.util.package_to_scan"))

    from .package_to_scan.module_to_scan import ClassItem, function_item

    assert result == [ClassItem, function_item]


def test_scan_package_with_predicate():
    from . import package_to_scan

    def predicate(arg):
        return inspect.isclass(arg)

    result = list(scan_packages(package_to_scan, predicate=predicate))

    from .package_to_scan.module_to_scan import ClassItem

    assert result == [ClassItem]


def test_scan_package_str_with_predicate():
    def predicate(arg):
        return inspect.isfunction(arg)

    result = list(scan_packages("tests.util.package_to_scan", predicate=predicate))

    from .package_to_scan.module_to_scan import function_item

    assert result == [function_item]


def test_non_function_predicate_should_fail():
    with pytest.raises(TypeError, match="invalid predicate"):
        list(scan_packages("", predicate="predicate"))
