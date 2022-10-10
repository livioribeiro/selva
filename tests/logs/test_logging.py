def test_module(capsys):
    from .modules import module

    captured = capsys.readouterr()
    assert captured.out == "tests.logs.modules.module\n"


def test_function(capsys):
    from .modules import function

    captured = capsys.readouterr()
    assert captured.out == "tests.logs.modules.function\n"


def test_class_property(capsys):
    from .modules import class_property

    captured = capsys.readouterr()
    assert captured.out == "tests.logs.modules.class_property\n"


def test_class_init(capsys):
    from .modules import class_init

    captured = capsys.readouterr()
    assert captured.out == "tests.logs.modules.class_init\n"


def test_class_static_method(capsys):
    from .modules import class_static_method

    captured = capsys.readouterr()
    assert captured.out == "tests.logs.modules.class_static_method\n"
