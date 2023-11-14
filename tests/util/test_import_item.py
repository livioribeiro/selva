import pytest

from selva._util.import_item import import_item


def test_import_item():
    item = import_item("tests.util.package_to_scan.module_to_scan.ClassItem")

    from .package_to_scan.module_to_scan import ClassItem

    assert item is ClassItem


@pytest.mark.parametrize("name", ["invalid", "invalid.module:item", ""])
def test_import_item_invalid_name_should_fail(name):
    with pytest.raises(ImportError, match="name must be in 'module.item' format"):
        import_item("invalid")
