import pytest

from selva._util.import_item import import_item


@pytest.mark.parametrize(
    "separator",
    [".", ":"],
    ids=["dot", "colon"],
)
def test_import_item(separator):
    item = import_item(f"tests.util.package_to_scan.module_to_scan{separator}ClassItem")

    from .package_to_scan.module_to_scan import ClassItem

    assert item is ClassItem


@pytest.mark.parametrize(
    "name",
    [
        "invalid",
        "invalid.item",
        "invalid:item",
        "invalid.module.item",
        "invalid.module:item",
        "",
    ],
)
def test_import_item_invalid_name_should_fail(name):
    with pytest.raises(ImportError):
        import_item("invalid")


@pytest.mark.parametrize(
    "separator",
    [".", ":"],
    ids=["dot", "colon"],
)
def test_import_missing_item_from_module_should_fail(separator):
    with pytest.raises(AttributeError):
        import_item(
            f"tests.util.package_to_scan.module_to_scan{separator}does_not_exist"
        )
